import random
import string
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from domain.entities.reservation import Reservation, SpecialRequest
from domain.entities.availability import Availability
from domain.entities.waitlist import WaitlistEntry
from domain.value_objects import DateRange, Money, GuestCount, CancellationPolicy
from domain.enums import ReservationStatus, BookingSource, RequestType, Priority, WaitlistStatus
from domain.repositories import ReservationRepository, AvailabilityRepository, WaitlistRepository

class ReservationService:
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        availability_repo: AvailabilityRepository,
        waitlist_repo: WaitlistRepository
    ):
        self.reservation_repo = reservation_repo
        self.availability_repo = availability_repo
        self.waitlist_repo = waitlist_repo

    def _generate_confirmation_code(self) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def _calculate_total_amount(self, check_in: date, check_out: date, rate_per_night: Decimal = Decimal("1000000")) -> Decimal:
        """Calculate total amount based on nights and rate"""
        nights = (check_out - check_in).days
        return rate_per_night * nights

    async def create_reservation(
        self,
        guest_id: UUID,
        room_type_id: str,
        check_in: date,
        check_out: date,
        adults: int,
        children: int,
        booking_source: BookingSource,
        special_requests: List[dict] = None,
        created_by: str = "SYSTEM"
    ) -> Reservation:
        """Create new reservation with validation"""
        if special_requests is None:
            special_requests = []

        # Create value objects
        date_range = DateRange(check_in=check_in, check_out=check_out)
        guest_count = GuestCount(adults=adults, children=children)
        total_amount = Money(
            amount=self._calculate_total_amount(check_in, check_out),
            currency="IDR"
        )

        cancellation_policy = CancellationPolicy(
            policy_name="Standard",
            refund_percentage=Decimal("80"),
            deadline_hours=24
        )

        # Create reservation
        confirmation_code = self._generate_confirmation_code()
        reservation = Reservation.create(
            guest_id=guest_id,
            room_type_id=room_type_id,
            date_range=date_range,
            guest_count=guest_count,
            total_amount=total_amount,
            cancellation_policy=cancellation_policy,
            booking_source=booking_source,
            confirmation_code=confirmation_code,
            created_by=created_by
        )

        # Add special requests if any
        for req in special_requests:
            req_type = RequestType(req.get("type", "OTHER"))
            reservation.add_special_request(req_type, req.get("description", ""))

        # Save to repository
        return await self.reservation_repo.save(reservation)

    async def get_reservation(self, reservation_id: UUID) -> Optional[Reservation]:
        return await self.reservation_repo.find_by_id(reservation_id)

    async def get_all_reservations(self) -> List[Reservation]:
        return await self.reservation_repo.find_all()

    async def get_reservations_by_guest(self, guest_id: UUID) -> List[Reservation]:
        return await self.reservation_repo.find_by_guest_id(guest_id)

    async def get_reservation_by_confirmation_code(self, code: str) -> Optional[Reservation]:
        return await self.reservation_repo.find_by_confirmation_code(code)

    async def modify_reservation(
        self,
        reservation_id: UUID,
        new_check_in: Optional[date] = None,
        new_check_out: Optional[date] = None,
        new_adults: Optional[int] = None,
        new_children: Optional[int] = None,
        new_room_type_id: Optional[str] = None
    ) -> Optional[Reservation]:
        """Modify reservation details"""
        reservation = await self.reservation_repo.find_by_id(reservation_id)
        if not reservation:
            return None

        # Build new objects if parameters provided
        new_date_range = None
        if new_check_in and new_check_out:
            new_date_range = DateRange(check_in=new_check_in, check_out=new_check_out)

        new_guest_count = None
        if new_adults is not None and new_children is not None:
            new_guest_count = GuestCount(adults=new_adults, children=new_children)

        new_total_amount = None
        if new_check_in and new_check_out:
            new_total_amount = Money(
                amount=self._calculate_total_amount(new_check_in, new_check_out),
                currency="IDR"
            )

        # Modify reservation
        reservation.modify(
            new_date_range=new_date_range,
            new_guest_count=new_guest_count,
            new_room_type_id=new_room_type_id,
            new_total_amount=new_total_amount
        )

        # Save updated reservation
        return await self.reservation_repo.update(reservation)

    async def add_special_request(
        self,
        reservation_id: UUID,
        request_type: str,
        description: str
    ) -> Optional[Reservation]:
        """Add special request to reservation"""
        reservation = await self.reservation_repo.find_by_id(reservation_id)
        if not reservation:
            return None

        req_type = RequestType(request_type)
        reservation.add_special_request(req_type, description)

        return await self.reservation_repo.update(reservation)

    async def confirm_reservation(
        self,
        reservation_id: UUID,
        payment_confirmed: bool = True
    ) -> Optional[Reservation]:
        """Confirm reservation after payment"""
        reservation = await self.reservation_repo.find_by_id(reservation_id)
        if not reservation:
            return None

        reservation.confirm(payment_confirmed)
        return await self.reservation_repo.update(reservation)

    async def check_in_guest(
        self,
        reservation_id: UUID,
        room_number: str
    ) -> Optional[Reservation]:
        """Mark guest as checked in"""
        reservation = await self.reservation_repo.find_by_id(reservation_id)
        if not reservation:
            return None

        reservation.check_in(room_number)
        return await self.reservation_repo.update(reservation)

    async def check_out_guest(self, reservation_id: UUID) -> Optional[Money]:
        """Process guest check-out"""
        reservation = await self.reservation_repo.find_by_id(reservation_id)
        if not reservation:
            return None

        final_amount = reservation.check_out()
        await self.reservation_repo.update(reservation)

        return final_amount

    async def cancel_reservation(
        self,
        reservation_id: UUID,
        reason: str = "Requested by guest"
    ) -> Optional[Money]:
        """Cancel reservation"""
        reservation = await self.reservation_repo.find_by_id(reservation_id)
        if not reservation:
            return None

        refund_amount = reservation.cancel(reason)
        await self.reservation_repo.update(reservation)

        return refund_amount

    async def mark_no_show(self, reservation_id: UUID) -> Optional[Reservation]:
        """Mark guest as no-show"""
        reservation = await self.reservation_repo.find_by_id(reservation_id)
        if not reservation:
            return None

        reservation.mark_no_show()
        return await self.reservation_repo.update(reservation)

class AvailabilityService:
    def __init__(self, availability_repo: AvailabilityRepository):
        self.availability_repo = availability_repo

    async def create_availability(
        self,
        room_type_id: str,
        availability_date: date,
        total_rooms: int,
        overbooking_threshold: int = 0
    ) -> Availability:
        """Create availability for a room type on a specific date"""
        availability = Availability(
            room_type_id=room_type_id,
            availability_date=availability_date,
            total_rooms=total_rooms,
            reserved_rooms=0,
            blocked_rooms=0,
            overbooking_threshold=overbooking_threshold
        )
        return await self.availability_repo.save(availability)

    async def get_availability(self, room_type_id: str, availability_date: date) -> Optional[Availability]:
        return await self.availability_repo.find_by_room_and_date(room_type_id, availability_date)

    async def check_availability(
        self,
        room_type_id: str,
        start_date: date,
        end_date: date,
        required_count: int
    ) -> bool:
        """Check if rooms are available for entire date range"""
        availabilities = await self.availability_repo.find_by_room_type(room_type_id, start_date, end_date)

        if not availabilities:
            return False

        for av in availabilities:
            if not av.check_availability(required_count):
                return False

        return True

    async def reserve_rooms(
        self,
        room_type_id: str,
        start_date: date,
        end_date: date,
        count: int
    ) -> bool:
        """Reserve rooms for a date range"""
        availabilities = await self.availability_repo.find_by_room_type(room_type_id, start_date, end_date)

        if not availabilities:
            return False

        for av in availabilities:
            av.reserve_rooms(count)
            await self.availability_repo.update(av)

        return True

    async def release_rooms(
        self,
        room_type_id: str,
        start_date: date,
        end_date: date,
        count: int
    ) -> bool:
        """Release rooms for a date range"""
        availabilities = await self.availability_repo.find_by_room_type(room_type_id, start_date, end_date)

        if not availabilities:
            return False

        for av in availabilities:
            av.release_rooms(count)
            await self.availability_repo.update(av)

        return True

    async def block_rooms(
        self,
        room_type_id: str,
        start_date: date,
        end_date: date,
        count: int,
        reason: str
    ) -> bool:
        """Block rooms for maintenance/events"""
        availabilities = await self.availability_repo.find_by_room_type(room_type_id, start_date, end_date)

        if not availabilities:
            return False

        for av in availabilities:
            av.block_rooms(count, reason)
            await self.availability_repo.update(av)

        return True

    async def unblock_rooms(
        self,
        room_type_id: str,
        start_date: date,
        end_date: date,
        count: int
    ) -> bool:
        """Unblock rooms after maintenance"""
        availabilities = await self.availability_repo.find_by_room_type(room_type_id, start_date, end_date)

        if not availabilities:
            return False

        for av in availabilities:
            av.unblock_rooms(count)
            await self.availability_repo.update(av)

        return True

class WaitlistService:
    def __init__(self, waitlist_repo: WaitlistRepository):
        self.waitlist_repo = waitlist_repo

    async def add_to_waitlist(
        self,
        guest_id: UUID,
        room_type_id: str,
        requested_dates: DateRange,
        guest_count: GuestCount,
        priority: Priority
    ) -> WaitlistEntry:
        """Add new entry to waitlist"""
        entry = WaitlistEntry.add_to_waitlist(
            guest_id=guest_id,
            room_type_id=room_type_id,
            requested_dates=requested_dates,
            guest_count=guest_count,
            priority=priority
        )
        return await self.waitlist_repo.save(entry)

    async def get_waitlist_entry(self, waitlist_id: UUID) -> Optional[WaitlistEntry]:
        return await self.waitlist_repo.find_by_id(waitlist_id)

    async def get_guest_waitlist(self, guest_id: UUID) -> List[WaitlistEntry]:
        return await self.waitlist_repo.find_by_guest_id(guest_id)

    async def get_room_waitlist(self, room_type_id: str) -> List[WaitlistEntry]:
        entries = await self.waitlist_repo.find_by_room_type(room_type_id)
        # Sort by priority score
        return sorted(entries, key=lambda x: x.calculate_priority_score(), reverse=True)

    async def get_active_waitlist(self) -> List[WaitlistEntry]:
        return await self.waitlist_repo.find_active_entries()

    async def convert_to_reservation(
        self,
        waitlist_id: UUID,
        reservation_id: UUID
    ) -> Optional[WaitlistEntry]:
        """Convert waitlist entry to actual reservation"""
        entry = await self.waitlist_repo.find_by_id(waitlist_id)
        if not entry:
            return None

        entry.convert_to_reservation(reservation_id)
        return await self.waitlist_repo.update(entry)

    async def expire_entry(self, waitlist_id: UUID) -> Optional[WaitlistEntry]:
        """Mark entry as expired"""
        entry = await self.waitlist_repo.find_by_id(waitlist_id)
        if not entry:
            return None

        entry.expire()
        return await self.waitlist_repo.update(entry)

    async def extend_expiry(self, waitlist_id: UUID, additional_days: int) -> Optional[WaitlistEntry]:
        """Extend expiry date"""
        entry = await self.waitlist_repo.find_by_id(waitlist_id)
        if not entry:
            return None

        entry.extend_expiry(additional_days)
        return await self.waitlist_repo.update(entry)

    async def upgrade_priority(
        self,
        waitlist_id: UUID,
        new_priority: Priority
    ) -> Optional[WaitlistEntry]:
        """Upgrade waitlist priority"""
        entry = await self.waitlist_repo.find_by_id(waitlist_id)
        if not entry:
            return None

        entry.upgrade_priority(new_priority)
        return await self.waitlist_repo.update(entry)

    async def mark_notified(self, waitlist_id: UUID) -> Optional[WaitlistEntry]:
        """Mark entry as notified"""
        entry = await self.waitlist_repo.find_by_id(waitlist_id)
        if not entry:
            return None

        entry.mark_notified()
        return await self.waitlist_repo.update(entry)

    async def get_entries_to_notify(self) -> List[WaitlistEntry]:
        """Get waitlist entries that need notification"""
        entries = await self.waitlist_repo.find_active_entries()
        return [e for e in entries if e.should_notify_again()]
