from typing import TypedDict, Optional
from app.models.ticket import TicketStatus

class TicketResponse(TypedDict):
    status: TicketStatus
    escalation_level: Optional[str]
    remaining_seconds: Optional[float]
