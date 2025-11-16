# domain/value_objects.py
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"

class DateRange(BaseModel):
    check_in: date
    check_out: date
    
    @validator('check_out')
    def check_out_after_check_in(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Check-out must be after check-in')
        return v
    
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
    
    class Config:
        frozen = True

class SpecialRequest(BaseModel):
    type: str
    description: str
    
    class Config:
        frozen = True

class CancellationPolicy(BaseModel):
    policy_name: str
    refund_percentage: Decimal = Field(ge=0, le=100)
    deadline_hours: int = Field(ge=0)
    
    class Config:
        frozen = True


# domain/entities.py
from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from domain.value_objects import (
    DateRange, Money, GuestCount, SpecialRequest, 
    CancellationPolicy, ReservationStatus
)

class Reservation(BaseModel):
    reservation_id: UUID = Field(default_factory=uuid4)
    confirmation_code: str
    guest_id: UUID
    room_type_id: UUID
    date_range: DateRange
    guest_count: GuestCount
    total_amount: Money
    status: ReservationStatus = ReservationStatus.PENDING
    special_requests: List[SpecialRequest] = []
    cancellation_policy: CancellationPolicy
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True


# domain/repositories.py
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from domain.entities import Reservation

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
    async def update(self, reservation: Reservation) -> Reservation:
        pass
    
    @abstractmethod
    async def delete(self, reservation_id: UUID) -> bool:
        pass


# infrastructure/in_memory_repository.py
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


# api/schemas.py
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from uuid import UUID
from typing import List, Optional

class DateRangeRequest(BaseModel):
    check_in: date
    check_out: date

class GuestCountRequest(BaseModel):
    adults: int = Field(ge=1, le=10)
    children: int = Field(ge=0, le=10)

class SpecialRequestRequest(BaseModel):
    type: str
    description: str

class CreateReservationRequest(BaseModel):
    guest_id: UUID
    room_type_id: UUID
    check_in: date
    check_out: date
    adults: int = Field(ge=1, le=10)
    children: int = Field(ge=0, le=10, default=0)
    special_requests: List[SpecialRequestRequest] = []

class UpdateReservationRequest(BaseModel):
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    adults: Optional[int] = Field(None, ge=1, le=10)
    children: Optional[int] = Field(None, ge=0, le=10)
    special_requests: Optional[List[SpecialRequestRequest]] = None

class ReservationResponse(BaseModel):
    reservation_id: UUID
    confirmation_code: str
    guest_id: UUID
    room_type_id: UUID
    check_in: date
    check_out: date
    adults: int
    children: int
    total_amount: Decimal
    currency: str
    status: str
    special_requests: List[dict]
    created_at: str


# application/services.py
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import random
import string
from domain.entities import Reservation
from domain.value_objects import (
    DateRange, Money, GuestCount, SpecialRequest,
    CancellationPolicy, ReservationStatus
)
from domain.repositories import ReservationRepository

class ReservationService:
    def __init__(self, repository: ReservationRepository):
        self.repository = repository
    
    def _generate_confirmation_code(self) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def _calculate_total_amount(self, check_in: str, check_out: str) -> Decimal:
        # Simplified calculation
        return Decimal("1000000")
    
    async def create_reservation(
        self,
        guest_id: UUID,
        room_type_id: UUID,
        check_in: str,
        check_out: str,
        adults: int,
        children: int,
        special_requests: List[dict]
    ) -> Reservation:
        date_range = DateRange(check_in=check_in, check_out=check_out)
        guest_count = GuestCount(adults=adults, children=children)
        total_amount = Money(
            amount=self._calculate_total_amount(check_in, check_out),
            currency="IDR"
        )
        
        special_req_objects = [
            SpecialRequest(type=req["type"], description=req["description"])
            for req in special_requests
        ]
        
        cancellation_policy = CancellationPolicy(
            policy_name="Standard",
            refund_percentage=Decimal("80"),
            deadline_hours=24
        )
        
        reservation = Reservation(
            confirmation_code=self._generate_confirmation_code(),
            guest_id=guest_id,
            room_type_id=room_type_id,
            date_range=date_range,
            guest_count=guest_count,
            total_amount=total_amount,
            special_requests=special_req_objects,
            cancellation_policy=cancellation_policy
        )
        
        return await self.repository.save(reservation)
    
    async def get_reservation(self, reservation_id: UUID) -> Optional[Reservation]:
        return await self.repository.find_by_id(reservation_id)
    
    async def get_all_reservations(self) -> List[Reservation]:
        return await self.repository.find_all()
    
    async def update_reservation(
        self,
        reservation_id: UUID,
        check_in: Optional[str],
        check_out: Optional[str],
        adults: Optional[int],
        children: Optional[int],
        special_requests: Optional[List[dict]]
    ) -> Optional[Reservation]:
        reservation = await self.repository.find_by_id(reservation_id)
        if not reservation:
            return None
        
        if check_in and check_out:
            reservation.date_range = DateRange(check_in=check_in, check_out=check_out)
        
        if adults is not None and children is not None:
            reservation.guest_count = GuestCount(adults=adults, children=children)
        
        if special_requests is not None:
            reservation.special_requests = [
                SpecialRequest(type=req["type"], description=req["description"])
                for req in special_requests
            ]
        
        reservation.updated_at = datetime.utcnow()
        return await self.repository.update(reservation)
    
    async def cancel_reservation(self, reservation_id: UUID) -> Optional[Reservation]:
        reservation = await self.repository.find_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.status = ReservationStatus.CANCELLED
        reservation.updated_at = datetime.utcnow()
        return await self.repository.update(reservation)


# main.py
from fastapi import FastAPI, HTTPException, Depends
from uuid import UUID
from typing import List
from api.schemas import (
    CreateReservationRequest,
    UpdateReservationRequest,
    ReservationResponse
)
from application.services import ReservationService
from infrastructure.in_memory_repository import InMemoryReservationRepository
from domain.repositories import ReservationRepository

app = FastAPI(title="Hotel Reservation API - Core Context")

repository = InMemoryReservationRepository()

def get_reservation_service() -> ReservationService:
    return ReservationService(repository)

@app.post("/api/reservations", response_model=ReservationResponse, status_code=201)
async def create_reservation(
    request: CreateReservationRequest,
    service: ReservationService = Depends(get_reservation_service)
):
    reservation = await service.create_reservation(
        guest_id=request.guest_id,
        room_type_id=request.room_type_id,
        check_in=str(request.check_in),
        check_out=str(request.check_out),
        adults=request.adults,
        children=request.children,
        special_requests=[req.dict() for req in request.special_requests]
    )
    
    return ReservationResponse(
        reservation_id=reservation.reservation_id,
        confirmation_code=reservation.confirmation_code,
        guest_id=reservation.guest_id,
        room_type_id=reservation.room_type_id,
        check_in=reservation.date_range.check_in,
        check_out=reservation.date_range.check_out,
        adults=reservation.guest_count.adults,
        children=reservation.guest_count.children,
        total_amount=reservation.total_amount.amount,
        currency=reservation.total_amount.currency,
        status=reservation.status.value,
        special_requests=[req.dict() for req in reservation.special_requests],
        created_at=reservation.created_at.isoformat()
    )

@app.get("/api/reservations/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: UUID,
    service: ReservationService = Depends(get_reservation_service)
):
    reservation = await service.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return ReservationResponse(
        reservation_id=reservation.reservation_id,
        confirmation_code=reservation.confirmation_code,
        guest_id=reservation.guest_id,
        room_type_id=reservation.room_type_id,
        check_in=reservation.date_range.check_in,
        check_out=reservation.date_range.check_out,
        adults=reservation.guest_count.adults,
        children=reservation.guest_count.children,
        total_amount=reservation.total_amount.amount,
        currency=reservation.total_amount.currency,
        status=reservation.status.value,
        special_requests=[req.dict() for req in reservation.special_requests],
        created_at=reservation.created_at.isoformat()
    )

@app.get("/api/reservations", response_model=List[ReservationResponse])
async def get_all_reservations(
    service: ReservationService = Depends(get_reservation_service)
):
    reservations = await service.get_all_reservations()
    return [
        ReservationResponse(
            reservation_id=r.reservation_id,
            confirmation_code=r.confirmation_code,
            guest_id=r.guest_id,
            room_type_id=r.room_type_id,
            check_in=r.date_range.check_in,
            check_out=r.date_range.check_out,
            adults=r.guest_count.adults,
            children=r.guest_count.children,
            total_amount=r.total_amount.amount,
            currency=r.total_amount.currency,
            status=r.status.value,
            special_requests=[req.dict() for req in r.special_requests],
            created_at=r.created_at.isoformat()
        )
        for r in reservations
    ]

@app.put("/api/reservations/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: UUID,
    request: UpdateReservationRequest,
    service: ReservationService = Depends(get_reservation_service)
):
    reservation = await service.update_reservation(
        reservation_id=reservation_id,
        check_in=str(request.check_in) if request.check_in else None,
        check_out=str(request.check_out) if request.check_out else None,
        adults=request.adults,
        children=request.children,
        special_requests=[req.dict() for req in request.special_requests] if request.special_requests else None
    )
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return ReservationResponse(
        reservation_id=reservation.reservation_id,
        confirmation_code=reservation.confirmation_code,
        guest_id=reservation.guest_id,
        room_type_id=reservation.room_type_id,
        check_in=reservation.date_range.check_in,
        check_out=reservation.date_range.check_out,
        adults=reservation.guest_count.adults,
        children=reservation.guest_count.children,
        total_amount=reservation.total_amount.amount,
        currency=reservation.total_amount.currency,
        status=reservation.status.value,
        special_requests=[req.dict() for req in reservation.special_requests],
        created_at=reservation.created_at.isoformat()
    )

@app.delete("/api/reservations/{reservation_id}")
async def cancel_reservation(
    reservation_id: UUID,
    service: ReservationService = Depends(get_reservation_service)
):
    reservation = await service.cancel_reservation(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return {"message": "Reservation cancelled successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)