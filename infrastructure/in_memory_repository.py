from typing import Optional, List, Dict
from uuid import UUID
from domain.entities import Reservation
from domain.repositories import ReservationRepository

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
