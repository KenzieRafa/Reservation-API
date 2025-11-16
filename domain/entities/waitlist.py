from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from datetime import datetime, timedelta, date
from typing import Optional
from domain.enums import Priority, WaitlistStatus
from domain.value_objects import DateRange, GuestCount

class WaitlistEntry(BaseModel):
    """Root Entity - Waitlist Aggregate"""
    # Identity
    waitlist_id: UUID = Field(default_factory=uuid4)

    # Request Details
    guest_id: UUID
    room_type_id: str
    requested_dates: DateRange
    guest_count: GuestCount

    # Status & Priority
    priority: Priority
    status: WaitlistStatus = WaitlistStatus.ACTIVE

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    notified_at: Optional[datetime] = None

    # Conversion
    converted_reservation_id: Optional[UUID] = None

    # Consistency Validation
    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        """Validate expires_at > created_at"""
        if 'created_at' in values:
            if v <= values['created_at']:
                raise ValueError('expires_at must be after created_at')
        return v

    @validator('guest_count')
    def validate_guest_count(cls, v):
        """Validate guest count"""
        if v.adults < 1:
            raise ValueError('At least 1 adult required')
        return v

    @validator('status')
    def validate_status_for_conversion(cls, v, values):
        """Validate status if converted"""
        if 'converted_reservation_id' in values and values['converted_reservation_id'] is not None:
            if v != WaitlistStatus.CONVERTED:
                raise ValueError('Status must be CONVERTED when reservation is converted')
        return v

    # Business Logic Methods

    @staticmethod
    def add_to_waitlist(
        guest_id: UUID,
        room_type_id: str,
        requested_dates: DateRange,
        guest_count: GuestCount,
        priority: Priority
    ) -> 'WaitlistEntry':
        """Add new entry to waitlist"""
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(days=14)

        return WaitlistEntry(
            guest_id=guest_id,
            room_type_id=room_type_id,
            requested_dates=requested_dates,
            guest_count=guest_count,
            priority=priority,
            status=WaitlistStatus.ACTIVE,
            created_at=created_at,
            expires_at=expires_at
        )

    def convert_to_reservation(self, reservation_id: UUID) -> None:
        """Convert waitlist entry to actual reservation"""
        # Validate status is ACTIVE
        if self.status != WaitlistStatus.ACTIVE:
            raise ValueError('Can only convert ACTIVE entries')

        # Change status to CONVERTED
        self.status = WaitlistStatus.CONVERTED
        # Record reservation_id
        self.converted_reservation_id = reservation_id

    def expire(self) -> None:
        """Mark entry as expired"""
        if self.status == WaitlistStatus.ACTIVE:
            self.status = WaitlistStatus.EXPIRED

    def extend_expiry(self, additional_days: int) -> None:
        """Extend expiry date"""
        if self.status == WaitlistStatus.ACTIVE:
            self.expires_at += timedelta(days=additional_days)

    def upgrade_priority(self, new_priority: Priority) -> None:
        """Upgrade to higher priority"""
        if new_priority.value > self.priority.value:
            self.priority = new_priority

    def mark_notified(self) -> None:
        """Record notification sent"""
        self.notified_at = datetime.utcnow()

    # Query Methods

    def should_notify_again(self) -> bool:
        """Check if time for reminder"""
        if not self.notified_at:
            return True

        days_since_notification = (datetime.utcnow() - self.notified_at).days
        return days_since_notification >= 3  # Remind every 3 days

    def calculate_priority_score(self) -> int:
        """Calculate priority score for ordering"""
        # Base score from priority enum
        score = self.priority.value * 100

        # Earlier request = higher score
        days_waiting = (datetime.utcnow() - self.created_at).days
        score += days_waiting * 2

        # Closer to expiry = higher urgency
        days_to_expiry = (self.expires_at - datetime.utcnow()).days
        score += (14 - days_to_expiry) * 5

        return score

    class Config:
        orm_mode = True
