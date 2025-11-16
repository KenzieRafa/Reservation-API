from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from typing import List, Optional

# Reservation Schemas
class SpecialRequestRequest(BaseModel):
    type: str
    description: str

class CreateReservationRequest(BaseModel):
    guest_id: UUID
    room_type_id: str
    check_in: date
    check_out: date
    adults: int = Field(ge=1, le=10)
    children: int = Field(ge=0, le=10, default=0)
    booking_source: str
    special_requests: List[SpecialRequestRequest] = []
    created_by: str = "SYSTEM"

class ModifyReservationRequest(BaseModel):
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    adults: Optional[int] = Field(None, ge=1, le=10)
    children: Optional[int] = Field(None, ge=0, le=10)
    room_type_id: Optional[str] = None

class AddSpecialRequestRequest(BaseModel):
    request_type: str
    description: str

class ConfirmReservationRequest(BaseModel):
    payment_confirmed: bool = True

class CheckInRequest(BaseModel):
    room_number: str

class CancelReservationRequest(BaseModel):
    reason: str = "Requested by guest"

class SpecialRequestResponse(BaseModel):
    request_id: UUID
    request_type: str
    description: str
    fulfilled: bool
    notes: Optional[str]
    created_at: datetime

class ReservationResponse(BaseModel):
    reservation_id: UUID
    confirmation_code: str
    guest_id: UUID
    room_type_id: str
    check_in: date
    check_out: date
    adults: int
    children: int
    total_amount: Decimal
    currency: str
    status: str
    booking_source: str
    special_requests: List[SpecialRequestResponse]
    created_at: datetime
    modified_at: datetime
    created_by: str
    version: int

class MoneyResponse(BaseModel):
    amount: Decimal
    currency: str

# Availability Schemas
class CreateAvailabilityRequest(BaseModel):
    room_type_id: str
    availability_date: date
    total_rooms: int = Field(ge=1)
    overbooking_threshold: int = Field(ge=0, default=0)

class AvailabilityResponse(BaseModel):
    room_type_id: str
    availability_date: date
    total_rooms: int
    reserved_rooms: int
    blocked_rooms: int
    available_rooms: int
    overbooking_threshold: int
    last_updated: datetime
    version: int

class CheckAvailabilityRequest(BaseModel):
    room_type_id: str
    start_date: date
    end_date: date
    required_count: int = Field(ge=1)

class ReserveRoomsRequest(BaseModel):
    room_type_id: str
    start_date: date
    end_date: date
    count: int = Field(ge=1)

class BlockRoomsRequest(BaseModel):
    room_type_id: str
    start_date: date
    end_date: date
    count: int = Field(ge=1)
    reason: str

# Waitlist Schemas
class CreateWaitlistRequest(BaseModel):
    guest_id: UUID
    room_type_id: str
    check_in: date
    check_out: date
    adults: int = Field(ge=1, le=10)
    children: int = Field(ge=0, le=10, default=0)
    priority: str

class WaitlistResponse(BaseModel):
    waitlist_id: UUID
    guest_id: UUID
    room_type_id: str
    check_in: date
    check_out: date
    adults: int
    children: int
    priority: str
    status: str
    created_at: datetime
    expires_at: datetime
    notified_at: Optional[datetime]
    converted_reservation_id: Optional[UUID]
    priority_score: int

class ConvertWaitlistRequest(BaseModel):
    reservation_id: UUID

class ExtendWaitlistRequest(BaseModel):
    additional_days: int = Field(ge=1)

class UpgradePriorityRequest(BaseModel):
    new_priority: str
