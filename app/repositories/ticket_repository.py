from typing import Optional, Sequence, Tuple
from sqlmodel import Session, select
from sqlalchemy import func

from app.models.ticket import Ticket, TicketStatus

class TicketRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        
    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self.session.exec(
            select(Ticket).where(Ticket.id == ticket_id)
        ).first()

    def get_open_tickets(self) -> Sequence[Ticket]:
        return self.session.exec(
            select(Ticket).where(Ticket.status == "OPEN")
        ).all()

    def save(self, ticket: Ticket) -> None:
        self.session.add(ticket)
        
    def get_paginated(
        self,
        *,
        status: Optional[TicketStatus] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[Sequence[Ticket], int]:
        offset = (page - 1) * page_size

        stmt = select(Ticket)
        if status is not None:
            stmt = stmt.where(Ticket.status == status)

        count_stmt = select(func.count()).select_from(Ticket)
        if status is not None:
            count_stmt = count_stmt.where(Ticket.status == status)
        total = self.session.exec(count_stmt).one()

        paginated = (
            self.session
            .exec(stmt.offset(offset).limit(page_size))
            .all()
        )

        return paginated, total