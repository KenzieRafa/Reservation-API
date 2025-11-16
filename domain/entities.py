from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from domain.value_objects import (
    DateRange, Money, GuestCount, SpecialRequest,
    CancellationPolicy, ReservationStatus
)

class Reservation(BaseModel):
    reservation_id: UUID = Field(default_factory=uuid4)
    confirmation_code: str
    guest_id: UUID
    room_type_id: UUID
    date_range: DateRange
    guest_count: GuestCount
    total_amount: Money
    status: ReservationStatus = ReservationStatus.PENDING
    special_requests: List[SpecialRequest] = []
    cancellation_policy: CancellationPolicy
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
