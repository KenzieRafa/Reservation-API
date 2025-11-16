from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from domain.enums import ReservationStatus, BookingSource, RequestType
from domain.value_objects import DateRange, Money, GuestCount, CancellationPolicy

class SpecialRequest(BaseModel):
    """Child Entity - SpecialRequest"""
    request_id: UUID = Field(default_factory=uuid4)
    request_type: RequestType
    description: str
    fulfilled: bool = False
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def fulfill(self, notes: str) -> None:
        """Mark request as fulfilled"""
        self.fulfilled = True
        self.notes = notes

    def is_fulfilled(self) -> bool:
        """Check if request is fulfilled"""
        return self.fulfilled

    class Config:
        orm_mode = True

class Reservation(BaseModel):
    """Root Entity - Reservation Aggregate"""
    # Identity
    reservation_id: UUID = Field(default_factory=uuid4)
    confirmation_code: str

    # References to other contexts
    guest_id: UUID
    room_type_id: str

    # Value Objects
    date_range: DateRange
    guest_count: GuestCount
    total_amount: Money
    cancellation_policy: CancellationPolicy

    # Enums/Status
    status: ReservationStatus = ReservationStatus.PENDING
    booking_source: BookingSource

    # Collections (child entities)
    special_requests: List[SpecialRequest] = []

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    version: int = 1

    # Consistency Validation
    @validator('date_range')
    def validate_date_range(cls, v):
        """Validate date range consistency rules"""
        nights = v.nights()
        if nights < 1:
            raise ValueError('Reservation must be at least 1 night')
        if nights > 30:
            raise ValueError('Maximum stay is 30 nights')
        return v

    @validator('guest_count')
    def validate_guest_count(cls, v):
        """Validate guest count consistency rules"""
        if v.adults < 1:
            raise ValueError('At least 1 adult required')
        if v.children < 0:
            raise ValueError('Children count cannot be negative')
        return v

    @validator('total_amount')
    def validate_amount(cls, v):
        """Validate amount consistency rules"""
        if v.amount <= 0:
            raise ValueError('Total amount must be greater than 0')
        return v

    # Business Logic Methods

    @classmethod
    def create(
        cls,
        guest_id: UUID,
        room_type_id: str,
        date_range: DateRange,
        guest_count: GuestCount,
        total_amount: Money,
        cancellation_policy: CancellationPolicy,
        booking_source: BookingSource,
        confirmation_code: str,
        created_by: str
    ) -> 'Reservation':
        """Create new reservation with validation"""
        # Validation happens through validators
        reservation = cls(
            guest_id=guest_id,
            room_type_id=room_type_id,
            date_range=date_range,
            guest_count=guest_count,
            total_amount=total_amount,
            cancellation_policy=cancellation_policy,
            status=ReservationStatus.PENDING,
            booking_source=booking_source,
            confirmation_code=confirmation_code,
            created_by=created_by
        )
        return reservation

    def modify(
        self,
        new_date_range: Optional[DateRange] = None,
        new_guest_count: Optional[GuestCount] = None,
        new_room_type_id: Optional[str] = None,
        new_total_amount: Optional[Money] = None
    ) -> None:
        """Modify reservation details"""
        # Check if modifiable
        if not self.is_modifiable():
            raise ValueError('Reservation cannot be modified in current state')

        if new_date_range:
            self.date_range = new_date_range

        if new_guest_count:
            self.guest_count = new_guest_count

        if new_room_type_id:
            self.room_type_id = new_room_type_id

        if new_total_amount:
            self.total_amount = new_total_amount

        self.modified_at = datetime.utcnow()
        self.version += 1

    def add_special_request(self, request_type: RequestType, description: str) -> None:
        """Add special request from guest"""
        special_request = SpecialRequest(
            request_type=request_type,
            description=description
        )
        self.special_requests.append(special_request)
        self.modified_at = datetime.utcnow()

    def confirm(self, payment_confirmed: bool) -> None:
        """Confirm reservation after payment"""
        if self.status != ReservationStatus.PENDING:
            raise ValueError('Can only confirm PENDING reservations')

        if not payment_confirmed:
            raise ValueError('Payment must be confirmed')

        self.status = ReservationStatus.CONFIRMED
        self.modified_at = datetime.utcnow()
        self.version += 1

    def check_in(self, room_number: str) -> None:
        """Mark guest as checked in"""
        if self.status != ReservationStatus.CONFIRMED:
            raise ValueError('Can only check in CONFIRMED reservations')

        if datetime.utcnow().date() < self.date_range.check_in:
            raise ValueError('Cannot check in before check-in date')

        self.status = ReservationStatus.CHECKED_IN
        self.modified_at = datetime.utcnow()
        self.version += 1

    def check_out(self) -> Money:
        """Process guest check-out"""
        if self.status != ReservationStatus.CHECKED_IN:
            raise ValueError('Can only check out CHECKED_IN reservations')

        self.status = ReservationStatus.CHECKED_OUT
        self.modified_at = datetime.utcnow()
        self.version += 1

        # Return final amount
        return self.total_amount

    def cancel(self, reason: str) -> Money:
        """Cancel reservation"""
        if not self.is_cancellable():
            raise ValueError('Reservation cannot be cancelled in current state')

        # Calculate refund using policy
        refund_amount = self.calculate_refund(date.today())

        self.status = ReservationStatus.CANCELLED
        self.modified_at = datetime.utcnow()
        self.version += 1

        return refund_amount

    def mark_no_show(self) -> None:
        """Mark guest as no-show"""
        if self.status not in [ReservationStatus.CONFIRMED, ReservationStatus.PENDING]:
            raise ValueError('Can only mark as no-show for PENDING or CONFIRMED reservations')

        self.status = ReservationStatus.NO_SHOW
        self.modified_at = datetime.utcnow()
        self.version += 1

    # Query Methods

    def is_modifiable(self) -> bool:
        """Check if reservation can be modified"""
        return (
            self.status in [ReservationStatus.PENDING, ReservationStatus.CONFIRMED]
            and self.date_range.check_in >= date.today() + timedelta(days=1)
        )

    def is_cancellable(self) -> bool:
        """Check if reservation can be cancelled"""
        return self.status in [ReservationStatus.PENDING, ReservationStatus.CONFIRMED]

    def calculate_refund(self, cancellation_date: date) -> Money:
        """Calculate refund amount based on policy"""
        return self.cancellation_policy.calculate_refund(
            self.total_amount,
            cancellation_date,
            self.date_range.check_in
        )

    def get_nights(self) -> int:
        """Get number of nights"""
        return self.date_range.nights()

    class Config:
        orm_mode = True
