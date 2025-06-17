# app/dto/dashboard_response.py
from pydantic import BaseModel
from typing import List
from app.dto.ticket_response import TicketResponse

class DashboardResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
