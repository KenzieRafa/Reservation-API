from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class DomainEvent(BaseModel):
    """Base class for domain events"""
    event_id: UUID
    event_type: str
    occurred_at: datetime
    aggregate_id: UUID
    aggregate_type: str

class ReservationCreated(DomainEvent):
    """Event published when reservation is created"""
    reservation_id: UUID
    guest_id: UUID
    room_type_id: str
    confirmation_code: str

class ReservationModified(DomainEvent):
    """Event published when reservation is modified"""
    reservation_id: UUID
    guest_id: UUID
    changes: dict  # What was changed

class ReservationConfirmed(DomainEvent):
    """Event published when reservation is confirmed"""
    reservation_id: UUID
    guest_id: UUID
    confirmation_code: str

class GuestCheckedIn(DomainEvent):
    """Event published when guest checks in"""
    reservation_id: UUID
    guest_id: UUID
    room_number: str
    check_in_time: datetime

class GuestCheckedOut(DomainEvent):
    """Event published when guest checks out"""
    reservation_id: UUID
    guest_id: UUID
    check_out_time: datetime
    final_amount: Decimal

class ReservationCancelled(DomainEvent):
    """Event published when reservation is cancelled"""
    reservation_id: UUID
    guest_id: UUID
    reason: str
    refund_amount: Decimal

class NoShowRecorded(DomainEvent):
    """Event published when guest is marked as no-show"""
    reservation_id: UUID
    guest_id: UUID
    room_type_id: str

class AvailabilityChanged(DomainEvent):
    """Event published when availability changes"""
    room_type_id: str
    availability_date: str
    available_rooms: int
    action: str  # reserve, release, block, unblock

class RoomsBlocked(DomainEvent):
    """Event published when rooms are blocked"""
    room_type_id: str
    count: int
    reason: str

class RoomsUnblocked(DomainEvent):
    """Event published when rooms are unblocked"""
    room_type_id: str
    count: int

class WaitlistEntryCreated(DomainEvent):
    """Event published when waitlist entry is created"""
    waitlist_id: UUID
    guest_id: UUID
    room_type_id: str
    priority: str

class WaitlistConverted(DomainEvent):
    """Event published when waitlist is converted to reservation"""
    waitlist_id: UUID
    guest_id: UUID
    reservation_id: UUID

class WaitlistExpired(DomainEvent):
    """Event published when waitlist entry expires"""
    waitlist_id: UUID
    guest_id: UUID

class WaitlistCancelled(DomainEvent):
    """Event published when waitlist entry is cancelled"""
    waitlist_id: UUID
    guest_id: UUID

class PriorityUpgraded(DomainEvent):
    """Event published when waitlist priority is upgraded"""
    waitlist_id: UUID
    guest_id: UUID
    new_priority: str
