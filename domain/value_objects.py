from pydantic import BaseModel, Field, validator
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID
from domain.enums import ReservationStatus, BookingSource, RequestType

class DateRange(BaseModel):
    check_in: date
    check_out: date

    @validator('check_out')
    def check_out_after_check_in(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Check-out must be after check-in')
        return v

    @validator('check_in')
    def check_in_not_past(cls, v):
        if v < date.today():
            raise ValueError('Check-in date cannot be in the past')
        return v

    def nights(self) -> int:
        """Calculate number of nights"""
        return (self.check_out - self.check_in).days

    class Config:
        frozen = True

class Money(BaseModel):
    amount: Decimal = Field(ge=0)
    currency: str = "IDR"

    class Config:
        frozen = True

class GuestCount(BaseModel):
    adults: int = Field(ge=1, le=10)
    children: int = Field(ge=0, le=10)

    @property
    def total_guests(self) -> int:
        """Get total number of guests"""
        return self.adults + self.children

    class Config:
        frozen = True

class CancellationPolicy(BaseModel):
    policy_name: str
    refund_percentage: Decimal = Field(ge=0, le=100)
    deadline_hours: int = Field(ge=0)

    def calculate_refund(self, total_amount: Money, cancellation_date: date, check_in_date: date) -> Money:
        """Calculate refund amount based on policy"""
        hours_until_checkin = (check_in_date - cancellation_date).days * 24

        if hours_until_checkin >= self.deadline_hours:
            refund_amount = total_amount.amount * (self.refund_percentage / 100)
        else:
            refund_amount = Decimal(0)

        return Money(amount=refund_amount, currency=total_amount.currency)

    class Config:
        frozen = True
