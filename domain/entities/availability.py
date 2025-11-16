from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional

class Availability(BaseModel):
    """Root Entity - Availability Aggregate (Denormalized)"""
    # Composite Identity
    room_type_id: str
    availability_date: date

    # Capacity Tracking
    total_rooms: int = Field(ge=0)
    reserved_rooms: int = Field(ge=0)
    blocked_rooms: int = Field(ge=0)

    # Configuration
    overbooking_threshold: int = Field(ge=0, default=0)

    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1

    # Consistency Validation
    @validator('reserved_rooms', 'blocked_rooms')
    def validate_capacity(cls, v, values):
        """Validate capacity consistency rules"""
        if 'total_rooms' in values:
            total = values['total_rooms']
            overbooking = values.get('overbooking_threshold', 0)
            max_allowed = total + overbooking

            reserved = values.get('reserved_rooms', 0)
            blocked = values.get('blocked_rooms', 0)

            if reserved + blocked > max_allowed:
                raise ValueError('reserved_rooms + blocked_rooms exceeds capacity')

        return v

    # Computed Properties

    @property
    def available_rooms(self) -> int:
        """Calculate available rooms"""
        return self.total_rooms - self.reserved_rooms - self.blocked_rooms

    @property
    def is_fully_booked(self) -> bool:
        """Check if no rooms available"""
        return self.available_rooms <= 0

    @property
    def can_overbook(self) -> bool:
        """Check if can accept overbooking"""
        current_overbooking = max(0, -self.available_rooms)
        return current_overbooking < self.overbooking_threshold

    # Business Logic Methods

    def check_availability(self, count: int) -> bool:
        """Check if can accommodate count rooms"""
        return self.available_rooms >= count or (
            self.available_rooms + self.overbooking_threshold >= count
        )

    def reserve_rooms(self, count: int) -> None:
        """Reserve rooms (decrease availability)"""
        # Validate capacity
        if not self.check_availability(count):
            raise ValueError('Insufficient availability')

        self.reserved_rooms += count
        self.last_updated = datetime.utcnow()
        self.version += 1

    def release_rooms(self, count: int) -> None:
        """Release rooms (increase availability)"""
        # Validate count
        if count > self.reserved_rooms:
            raise ValueError('Cannot release more than reserved')

        self.reserved_rooms -= count
        self.last_updated = datetime.utcnow()
        self.version += 1

    def block_rooms(self, count: int, reason: str) -> None:
        """Block rooms for maintenance/events"""
        # Validate capacity
        if self.blocked_rooms + count > self.total_rooms:
            raise ValueError('Cannot block more rooms than total available')

        self.blocked_rooms += count
        self.last_updated = datetime.utcnow()
        self.version += 1

    def unblock_rooms(self, count: int) -> None:
        """Unblock rooms after maintenance"""
        if count > self.blocked_rooms:
            raise ValueError('Cannot unblock more than blocked')

        self.blocked_rooms -= count
        self.last_updated = datetime.utcnow()
        self.version += 1

    class Config:
        orm_mode = True
