from typing import Optional, List, Dict, Tuple
from uuid import UUID
from datetime import date
from domain.entities.reservation import Reservation
from domain.entities.availability import Availability
from domain.entities.waitlist import WaitlistEntry
from domain.repositories import ReservationRepository, AvailabilityRepository, WaitlistRepository

class InMemoryReservationRepository(ReservationRepository):
    def __init__(self):
        self._storage: Dict[UUID, Reservation] = {}

    async def save(self, reservation: Reservation) -> Reservation:
        self._storage[reservation.reservation_id] = reservation
        return reservation

    async def find_by_id(self, reservation_id: UUID) -> Optional[Reservation]:
        return self._storage.get(reservation_id)

    async def find_by_confirmation_code(self, code: str) -> Optional[Reservation]:
        for reservation in self._storage.values():
            if reservation.confirmation_code == code:
                return reservation
        return None

    async def find_all(self) -> List[Reservation]:
        return list(self._storage.values())

    async def find_by_guest_id(self, guest_id: UUID) -> List[Reservation]:
        return [r for r in self._storage.values() if r.guest_id == guest_id]

    async def update(self, reservation: Reservation) -> Reservation:
        if reservation.reservation_id in self._storage:
            self._storage[reservation.reservation_id] = reservation
            return reservation
        raise ValueError("Reservation not found")

    async def delete(self, reservation_id: UUID) -> bool:
        if reservation_id in self._storage:
            del self._storage[reservation_id]
            return True
        return False

class InMemoryAvailabilityRepository(AvailabilityRepository):
    def __init__(self):
        self._storage: Dict[Tuple[str, date], Availability] = {}

    async def save(self, availability: Availability) -> Availability:
        key = (availability.room_type_id, availability.availability_date)
        self._storage[key] = availability
        return availability

    async def find_by_room_and_date(self, room_type_id: str, availability_date: date) -> Optional[Availability]:
        key = (room_type_id, availability_date)
        return self._storage.get(key)

    async def find_by_room_type(self, room_type_id: str, start_date: date, end_date: date) -> List[Availability]:
        result = []
        for (room_id, av_date), availability in self._storage.items():
            if room_id == room_type_id and start_date <= av_date <= end_date:
                result.append(availability)
        return result

    async def update(self, availability: Availability) -> Availability:
        key = (availability.room_type_id, availability.availability_date)
        if key in self._storage:
            self._storage[key] = availability
            return availability
        raise ValueError("Availability not found")

    async def delete(self, room_type_id: str, availability_date: date) -> bool:
        key = (room_type_id, availability_date)
        if key in self._storage:
            del self._storage[key]
            return True
        return False

class InMemoryWaitlistRepository(WaitlistRepository):
    def __init__(self):
        self._storage: Dict[UUID, WaitlistEntry] = {}

    async def save(self, waitlist_entry: WaitlistEntry) -> WaitlistEntry:
        self._storage[waitlist_entry.waitlist_id] = waitlist_entry
        return waitlist_entry

    async def find_by_id(self, waitlist_id: UUID) -> Optional[WaitlistEntry]:
        return self._storage.get(waitlist_id)

    async def find_by_guest_id(self, guest_id: UUID) -> List[WaitlistEntry]:
        return [w for w in self._storage.values() if w.guest_id == guest_id]

    async def find_by_room_type(self, room_type_id: str) -> List[WaitlistEntry]:
        return [w for w in self._storage.values() if w.room_type_id == room_type_id]

    async def find_active_entries(self) -> List[WaitlistEntry]:
        from domain.enums import WaitlistStatus
        return [w for w in self._storage.values() if w.status == WaitlistStatus.ACTIVE]

    async def update(self, waitlist_entry: WaitlistEntry) -> WaitlistEntry:
        if waitlist_entry.waitlist_id in self._storage:
            self._storage[waitlist_entry.waitlist_id] = waitlist_entry
            return waitlist_entry
        raise ValueError("Waitlist entry not found")

    async def delete(self, waitlist_id: UUID) -> bool:
        if waitlist_id in self._storage:
            del self._storage[waitlist_id]
            return True
        return False
