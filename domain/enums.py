from enum import Enum

class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"

class BookingSource(str, Enum):
    ONLINE = "ONLINE"
    PHONE = "PHONE"
    WALK_IN = "WALK_IN"
    PARTNER = "PARTNER"

class RequestType(str, Enum):
    EARLY_CHECKIN = "EARLY_CHECKIN"
    LATE_CHECKOUT = "LATE_CHECKOUT"
    HIGH_FLOOR = "HIGH_FLOOR"
    LOW_FLOOR = "LOW_FLOOR"
    SMOKING = "SMOKING"
    NON_SMOKING = "NON_SMOKING"
    SPECIAL_AMENITIES = "SPECIAL_AMENITIES"
    OTHER = "OTHER"

class Priority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class WaitlistStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CONVERTED = "CONVERTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
