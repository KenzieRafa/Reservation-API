from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from datetime import date
from domain.entities.reservation import Reservation
from domain.entities.availability import Availability
from domain.entities.waitlist import WaitlistEntry

class ReservationRepository(ABC):
    @abstractmethod
    async def save(self, reservation: Reservation) -> Reservation:
        pass

    @abstractmethod
    async def find_by_id(self, reservation_id: UUID) -> Optional[Reservation]:
        pass

    @abstractmethod
    async def find_by_confirmation_code(self, code: str) -> Optional[Reservation]:
        pass

    @abstractmethod
    async def find_all(self) -> List[Reservation]:
        pass

    @abstractmethod
    async def find_by_guest_id(self, guest_id: UUID) -> List[Reservation]:
        pass

    @abstractmethod
    async def update(self, reservation: Reservation) -> Reservation:
        pass

    @abstractmethod
    async def delete(self, reservation_id: UUID) -> bool:
        pass

class AvailabilityRepository(ABC):
    @abstractmethod
    async def save(self, availability: Availability) -> Availability:
        pass

    @abstractmethod
    async def find_by_room_and_date(self, room_type_id: str, availability_date: date) -> Optional[Availability]:
        pass

    @abstractmethod
    async def find_by_room_type(self, room_type_id: str, start_date: date, end_date: date) -> List[Availability]:
        pass

    @abstractmethod
    async def update(self, availability: Availability) -> Availability:
        pass

    @abstractmethod
    async def delete(self, room_type_id: str, availability_date: date) -> bool:
        pass

class WaitlistRepository(ABC):
    @abstractmethod
    async def save(self, waitlist_entry: WaitlistEntry) -> WaitlistEntry:
        pass

    @abstractmethod
    async def find_by_id(self, waitlist_id: UUID) -> Optional[WaitlistEntry]:
        pass

    @abstractmethod
    async def find_by_guest_id(self, guest_id: UUID) -> List[WaitlistEntry]:
        pass

    @abstractmethod
    async def find_by_room_type(self, room_type_id: str) -> List[WaitlistEntry]:
        pass

    @abstractmethod
    async def find_active_entries(self) -> List[WaitlistEntry]:
        pass

    @abstractmethod
    async def update(self, waitlist_entry: WaitlistEntry) -> WaitlistEntry:
        pass

    @abstractmethod
    async def delete(self, waitlist_id: UUID) -> bool:
        pass
