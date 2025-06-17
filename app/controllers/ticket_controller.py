from fastapi import APIRouter, Query, Response
from typing import List, Optional
from app.dto.dashboard_response import DashboardResponse
from app.models.ticket import Ticket, TicketStatus
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])
ticket_service = TicketService()

@router.post("/", status_code=201)
def ingest_tickets(tickets: List[Ticket], response: Response):
    ticket_service.process_tickets(tickets)
    return {"message": "Tickets processed"}

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    status_code=200,
    summary="Tickets dashboard filtered and paginated",
)
def get_dashboard(
    status: Optional[TicketStatus] = Query(
        None,
        description="Filter by status (0=OPEN, 1=ONGOING, 2=CLOSED)",
    ),
    page: int = Query(1, ge=1, description="Page number (starts in 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    tickets, total = ticket_service.get_tickets_paginated(
        status=status,
        page=page,
        page_size=page_size,
    )
    return DashboardResponse(tickets=tickets, total=total)

@router.get("/{ticket_id}", status_code=200)
def get_ticket_by_id(ticket_id: int):
    return ticket_service.get_ticket_by_id(ticket_id)

# If you want to use to test the escalate-workflow more easily uncomment this
# @router.get("/escalate-workflow", status_code=200)
# def escalate_workflow(response: Response):
#     ticket_service.escalate_workflow()
#     return {"message": "Workflow escalated"}