from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, Index, Integer, func
from sqlmodel import SQLModel, Field
from enum import IntEnum
from typing import Optional

class Priority(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class CustomerTier(IntEnum):
    BRONZE = 0
    SILVER = 1
    GOLD = 2
    PLATINUM = 3
    
class TicketStatus(IntEnum):
    OPEN = 0
    ONGOING = 1
    CLOSED = 2


class Ticket(SQLModel, table=True):
    __table_args__ = (
        Index("ix_ticket_priority", "priority"),
        Index("ix_ticket_customer_tier", "customer_tier"),
    )

    id: int = Field(default=None, sa_column=Column(Integer, primary_key=True, autoincrement=False, nullable=False))

    priority: Optional[Priority] = Field(
        default=Priority.LOW,
        sa_column=Column(Enum(Priority, name="priority_enum"), nullable=False)
    )

    customer_tier: Optional[CustomerTier] = Field(
        default=None,
        sa_column=Column(Enum(CustomerTier, name="customer_tier_enum"), nullable=True)
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    )

    status: Optional[TicketStatus] = Field(
        default=None,
        sa_column=Column(Enum(TicketStatus, name="ticket_status_enum"), nullable=False, default=0)
    )

    escalation_level: Optional[str]
    resolved_at: Optional[datetime] = Field(default=None)
    response_sla_deadline: datetime = Field(default=None, nullable=False)
    resolution_sla_deadline: Optional[datetime] = Field(default=None, nullable=False)
    
