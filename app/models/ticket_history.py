from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, DateTime, Enum
from sqlmodel import Field, SQLModel

from app.models.ticket import CustomerTier, Priority, TicketStatus


class TicketHistory(SQLModel, table=True):
    __tablename__ = "ticket_history" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: Optional[int]

    priority: Optional[Priority] = Field(
        default=Priority.LOW,
        sa_column=Column(Enum(Priority, name="priority_enum"), nullable=False)
    )

    customer_tier: Optional[CustomerTier] = Field(
        default=None,
        sa_column=Column(Enum(CustomerTier, name="customer_tier_enum"), nullable=True)
    )
    
    status: Optional[TicketStatus] = Field(
        default=None,
        sa_column=Column(Enum(TicketStatus, name="ticket_status_enum"), nullable=False, default=0)
    )

    created_at: datetime
    updated_at: datetime

    changed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    change_type: str  # e.g., "UPDATE", "DELETE"