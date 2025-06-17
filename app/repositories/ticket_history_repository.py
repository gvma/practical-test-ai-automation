from datetime import datetime, timezone
from sqlmodel import Session

from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory

class TicketHistoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, ticket: Ticket, change_type: str = "UPDATE") -> None:
        history = TicketHistory(
            ticket_id=ticket.id,
            priority=ticket.priority,
            customer_tier=ticket.customer_tier,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            status=ticket.status,
            changed_at=datetime.now(timezone.utc),
            change_type=change_type
        )
        self.session.add(history)