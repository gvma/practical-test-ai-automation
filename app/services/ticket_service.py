import json
from asyncio.log import logger
from typing import List, Optional, Sequence, Tuple
from datetime import datetime, timezone

from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.db import engine
from app.dto.ticket_response import TicketResponse
from app.exceptions.exceptions import DBException, NotFoundException, UnexpectedException, UseCaseException
from app.models.ticket import EscalationLevel, Ticket, TicketStatus
from app.repositories.ticket_history_repository import TicketHistoryRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.webhooks.slack_webhook_service import SlackWebhook
from app.utils.utils import calculate_remaining_seconds, to_datetime
from app.websocket.manager import manager


class TicketService:
    def __init__(self):
        pass

    def get_ticket_by_id(self, ticket_id: int) -> TicketResponse:
        logger.info(f"Fetching ticket by id: {ticket_id}")
        with Session(engine) as session:
            try:
                ticket = TicketRepository(session).get_by_id(ticket_id)
                if ticket is None:
                    logger.warning(f"Ticket {ticket_id} not found")
                    raise NotFoundException("Ticket not found.")

                if ticket.escalation_level is None:
                    logger.error(f"Invalid ticket state for id {ticket_id}: status or escalation_level is None")
                    raise UnexpectedException("Ticket has incomplete data.")

                remaining_time = calculate_remaining_seconds(
                    ticket.created_at,
                    ticket.resolution_sla_deadline
                )
                logger.info(f"Ticket {ticket_id} fetched: status={ticket.status}, remaining_seconds={remaining_time}")

                return TicketResponse(
                    status=ticket.status,
                    escalation_level=ticket.escalation_level,
                    remaining_seconds=remaining_time
                )

            except NotFoundException:
                raise
            except Exception as general_error:
                logger.exception(f"Unexpected error fetching ticket {ticket_id}: {general_error}")
                raise UnexpectedException(f"Unexpected error fetching ticket: {general_error}")

    def process_tickets(self, tickets: List[Ticket]) -> None:
        logger.info(f"Starting to process batch of {len(tickets)} tickets")
        try:
            with Session(engine) as session:
                repo = TicketRepository(session)

                for ticket in tickets:
                    try:
                        logger.info(f"Processing ticket id={ticket.id}")
                        self._process_single_ticket(ticket, repo, session)
                    except SQLAlchemyError as db_err:
                        logger.exception(f"Database error processing ticket {ticket.id}: {db_err}")
                        session.rollback()
                        raise DBException("Error processing tickets")

                session.commit()
                logger.info("All tickets processed and session committed")

        except (DBException, UseCaseException):
            logger.warning("Process halted due to known exception")
            raise
        except Exception as general_error:
            logger.exception(f"Unexpected error processing tickets: {general_error}")
            raise UnexpectedException(f"Unexpected error processing tickets: {general_error}")

    def _process_single_ticket(
        self,
        ticket: Ticket,
        repo: TicketRepository,
        session: Session
    ) -> None:
        self._validate_ticket_id(ticket)
        ticket.updated_at = to_datetime(ticket.updated_at)

        existing = repo.get_by_id(ticket.id)
        if existing:
            logger.info(f"Existing ticket found: id={ticket.id}, updated_at={existing.updated_at}")
            if self._is_same_update(existing, ticket):
                logger.info(f"No changes detected for ticket {ticket.id}, skipping")
                return

            self._save_history(ticket, session)
            self._update_existing_ticket(existing, ticket)
            logger.info(f"Updated ticket {ticket.id}")
        else:
            repo.save(ticket)
            logger.info(f"Saved new ticket {ticket.id}")

    def _validate_ticket_id(self, ticket: Ticket) -> None:
        ticket_id = getattr(ticket, "id", None)
        if ticket_id is None:
            logger.error("Ticket id is missing in incoming data")
            raise UseCaseException("Id missing")

    def _is_same_update(self, existing: Ticket, incoming: Ticket) -> bool:
        return (
            existing.updated_at.isoformat(timespec="seconds")
            == incoming.updated_at.isoformat(timespec="seconds")
        )

    def _save_history(self, ticket: Ticket, session: Session) -> None:
        logger.info(f"Saving history for ticket {ticket.id}")
        TicketHistoryRepository(session).save(ticket)

    def _update_existing_ticket(self, existing: Ticket, incoming: Ticket) -> None:
        existing.priority = incoming.priority
        existing.updated_at = incoming.updated_at
        existing.created_at = incoming.created_at
        existing.status = incoming.status
        existing.customer_tier = incoming.customer_tier

    def escalate_workflow(self) -> None:
        logger.info("Starting escalation workflow")
        with Session(engine) as session:
            try:
                tickets: Sequence[Ticket] = self._fetch_open_tickets(session)
                logger.info(f"Found {len(tickets)} open tickets to evaluate")
                for ticket in tickets:
                    self._process_ticket(ticket)
                session.commit()
                logger.info("Escalation workflow completed")
            except Exception as e:
                session.rollback()
                logger.exception(f"Error escalating workflow: {e}")
                raise UnexpectedException(f"Error escalating: {e}")

    def get_tickets_paginated(
        self,
        *,
        status: Optional[TicketStatus] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[TicketResponse], int]:
        logger.info(f"Fetching tickets page={page}, size={page_size}, status={status}")
        try:
            with Session(engine) as session:
                repo = TicketRepository(session)
                tickets, total = repo.get_paginated(
                    status=status, page=page, page_size=page_size
                )

                responses: List[TicketResponse] = []
                for t in tickets:
                    remaining = calculate_remaining_seconds(
                        t.created_at, t.resolution_sla_deadline
                    )
                    responses.append(
                        TicketResponse(
                            status=t.status,
                            escalation_level=t.escalation_level,
                            remaining_seconds=remaining,
                        )
                    )

                logger.info(f"Returning {len(responses)} tickets out of total {total}")
                return responses, total

        except SQLAlchemyError as db_err:
            logger.exception(f"Database error fetching paginated tickets: {db_err}")
            raise DBException("Database error fetching tickets")
        except Exception as err:
            logger.exception(f"Unexpected error fetching paginated tickets: {err}")
            raise UnexpectedException(f"Unexpected error fetching tickets: {err}")

    def _fetch_open_tickets(self, session: Session) -> Sequence[Ticket]:
        logger.info("Querying open tickets from repository")
        return TicketRepository(session).get_open_tickets()

    def _process_ticket(self, ticket: Ticket) -> None:
        if ticket.resolution_sla_deadline is None:
            logger.info(f"Ticket {ticket.id} has no SLA deadline, skipping")
            return

        created_at, deadline = self._ensure_timezone(
            ticket.created_at, ticket.resolution_sla_deadline
        )
        remaining_percent: float = self._calculate_remaining_percent(created_at, deadline)

        if 0 < remaining_percent <= 15:
            self._handle_alert(ticket, remaining_percent)
        elif remaining_percent <= 0:
            self._handle_breach(ticket, remaining_percent)

    def _ensure_timezone(
        self, created_at: datetime, deadline: datetime
    ) -> Tuple[datetime, datetime]:
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        return created_at, deadline

    def _calculate_remaining_percent(
        self, created_at: datetime, deadline: datetime
    ) -> float:
        total_seconds = (deadline - created_at).total_seconds()
        remaining_seconds = calculate_remaining_seconds(created_at, deadline)
        return 100.0 - ((remaining_seconds / total_seconds) * 100.0)
    
    def _send_slack_webhook(self, ticket_id: int, remaining_percent: float) -> None:
        slack_webhook = SlackWebhook()
        response = slack_webhook.send_alert(ticket_id, remaining_percent)
        data = response.json()
        logger.info(f"[Slack] webhook response for ticket {ticket_id}:\n{json.dumps(data, indent=2)}")

    def _handle_alert(self, ticket: Ticket, remaining_percent: float) -> None:
        logger.info(f"[ALERT] Ticket {ticket.id}: {remaining_percent:.2f}% SLA remaining")
        ticket.escalation_level = EscalationLevel.ALERT
        self._send_slack_webhook(ticket.id, remaining_percent)
        self._schedule_broadcast(ticket.id, "ALERT", remaining_percent)

    def _handle_breach(self, ticket: Ticket, remaining_percent: float) -> None:
        logger.info(f"[BREACH] Ticket {ticket.id}: SLA violated")
        ticket.escalation_level = EscalationLevel.BREACH
        self._send_slack_webhook(ticket.id, remaining_percent)
        self._schedule_broadcast(ticket.id, "BREACH", remaining_percent)

    def _schedule_broadcast(self, ticket_id: int, event: str, remaining_percent: float):
        payload = json.dumps({
            "event": event,
            "ticket_id": ticket_id,
            "remaining_percent": remaining_percent,
        })
        manager.schedule_broadcast(payload)
