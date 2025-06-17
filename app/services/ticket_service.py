import json
from asyncio.log import logger
from typing import List, Optional, Sequence, Tuple
from datetime import datetime, timezone

from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.db import engine
from app.dto.ticket_response import TicketResponse
from app.exceptions.exceptions import DBException, NotFoundException, UnexpectedException, UseCaseException
from app.models.ticket import Ticket, TicketStatus
from app.repositories.ticket_history_repository import TicketHistoryRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.webhooks.slack_webhook_service import SlackWebhook
from app.utils.utils import calculate_remaining_seconds, to_datetime
from app.websocket.manager import manager


def send_slack_webhook(ticket_id: int, remaining_percent: float) -> None:
    slack_webhook = SlackWebhook()
    response = slack_webhook.send_alert(ticket_id, remaining_percent)
    data = response.json()
    logger.info(json.dumps(data, indent=2))


class TicketService:
    def __init__(self):
        pass

    def get_ticket_by_id(self, ticket_id: int) -> TicketResponse:
        with Session(engine) as session:
            try:
                ticket = TicketRepository(session).get_by_id(ticket_id)
                if ticket is None:
                    raise NotFoundException("Ticket not found.")

                remaining_time = calculate_remaining_seconds(
                    ticket.created_at,
                    ticket.resolution_sla_deadline
                )

                return TicketResponse(
                    status=ticket.status,
                    escalation_level=ticket.escalation_level,
                    remaining_seconds=remaining_time
                )

            except NotFoundException:
                raise
            except Exception as general_error:
                logger.exception(f"Unexpected error fetching ticket: {general_error}")
                raise UnexpectedException(f"Unexpected error fetching ticket: {general_error}")

    def process_tickets(self, tickets: List[Ticket]) -> None:
        try:
            with Session(engine) as session:
                repo = TicketRepository(session)

                for ticket in tickets:
                    try:
                        if ticket.id is None:
                            raise UseCaseException("Id missing")

                        ticket.updated_at = to_datetime(ticket.updated_at)
                        existing = repo.get_by_id(ticket.id)

                        if existing:
                            if (existing.updated_at.isoformat(timespec="seconds") ==
                                    ticket.updated_at.isoformat(timespec="seconds")):
                                continue

                            TicketHistoryRepository(session).save(ticket)

                            existing.priority = ticket.priority
                            existing.updated_at = ticket.updated_at
                            existing.created_at = ticket.created_at
                            existing.status = ticket.status
                            existing.customer_tier = ticket.customer_tier
                        else:
                            repo.save(ticket)

                    except SQLAlchemyError as db_error:
                        logger.exception(f"Error processing ticket {ticket.id}: {db_error}")
                        session.rollback()
                        raise DBException("Error processing tickets")

                session.commit()

        except (DBException, UseCaseException):
            raise
        except Exception as general_error:
            logger.exception(f"Unexpected error processing tickets: {general_error}")
            raise UnexpectedException(f"Unexpected error processing tickets: {general_error}")

    def escalate_workflow(self) -> None:
        with Session(engine) as session:
            try:
                tickets: Sequence[Ticket] = self._fetch_open_tickets(session)
                for ticket in tickets:
                    self._process_ticket(ticket)
                session.commit()
            except Exception as e:
                session.rollback()
                logger.exception(f"Error escalating workflow: {e}")
                raise UnexpectedException(f"Erro escalating: {e}")

    def get_tickets_paginated(
        self,
        *,
        status: Optional[TicketStatus] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[TicketResponse], int]:
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

                return responses, total

        except SQLAlchemyError as db_err:
            logger.exception(f"Erro ao buscar tickets paginados: {db_err}")
            raise DBException("Erro de banco ao buscar tickets")
        except Exception as err:
            logger.exception(f"Erro inesperado ao buscar tickets: {err}")
            raise UnexpectedException(f"Erro inesperado ao buscar tickets: {err}")

    def _fetch_open_tickets(self, session: Session) -> Sequence[Ticket]:
        return TicketRepository(session).get_open_tickets()

    def _process_ticket(self, ticket: Ticket) -> None:
        if ticket.resolution_sla_deadline is None:
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

    def _handle_alert(self, ticket: Ticket, remaining_percent: float) -> None:
        ticket.escalation_level = "ALERT"
        logger.info(
            f"[ALERT] Ticket {ticket.id} with {remaining_percent:.2f}% SLA time remaining."
        )
        send_slack_webhook(ticket.id, remaining_percent)
        self._schedule_broadcast(ticket.id, "ALERT", remaining_percent)

    def _handle_breach(self, ticket: Ticket, remaining_percent: float) -> None:
        ticket.escalation_level = "BREACH"
        logger.info(f"[BREACH] Ticket {ticket.id} violated the SLA.")
        send_slack_webhook(ticket.id, remaining_percent)
        self._schedule_broadcast(ticket.id, "BREACH", remaining_percent)
        
    def _schedule_broadcast(self, ticket_id: int, event: str, remaining_percent: float):
        payload = json.dumps({
            "event": event,
            "ticket_id": ticket_id,
            "remaining_percent": remaining_percent,
        })
        manager.schedule_broadcast(payload)

