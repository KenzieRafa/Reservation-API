# Hotel Reservation API - Domain-Driven Design Implementation

Implementasi lengkap Hotel Reservation System menggunakan Domain-Driven Design (DDD) dengan FastAPI dan Pydantic.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Running the Server](#running-the-server)
- [Testing with Postman](#testing-with-postman)
- [API Endpoints](#api-endpoints)
- [Enum Reference](#enum-reference)
- [Troubleshooting](#troubleshooting)

---

## 📌 Project Overview

Sistem reservasi hotel dengan 3 Aggregates utama:
- **Reservation Aggregate**: Manajemen pemesanan kamar dengan validasi bisnis lengkap
- **Availability Aggregate**: Tracking ketersediaan kamar dan overbooking
- **Waitlist Aggregate**: Daftar tunggu dengan prioritas dan notifikasi

**Total Endpoints**: 33 endpoints (12 Reservation, 7 Availability, 11 Waitlist + Health & Enum Reference)

---

## 🛠 Tech Stack

| Komponen | Version |
|----------|---------|
| Python | 3.8+ |
| FastAPI | 0.104.1+ |
| Uvicorn | 0.24.0+ |
| Pydantic | 2.5.0+ |

---

## 📁 Project Structure

```
TST TUBES MILESTONE 4/
├── main.py                          # FastAPI application entry point
├── Reservation.py                   # Legacy monolithic file (reference)
├── requirements.txt                 # Python dependencies
├── POSTMAN_COLLECTION.json         # Complete API testing collection
├── README.md                        # This file
│
├── domain/                          # Domain Layer (Business Logic)
│   ├── __init__.py
│   ├── enums.py                    # All enum definitions
│   ├── entities.py                 # Aggregate roots (Reservation, Availability, WaitlistEntry)
│   ├── repositories.py             # Repository interfaces
│   ├── value_objects.py            # Value objects (DateRange, Money, GuestCount, etc)
│   └── events.py                   # Domain events
│
├── application/                     # Application Layer (Use Cases)
│   ├── __init__.py
│   └── services.py                 # Business services
│
├── infrastructure/                  # Infrastructure Layer (Data Persistence)
│   ├── __init__.py
│   └── repositories/
│       ├── __init__.py
│       └── in_memory_repositories.py  # In-memory implementations
│
└── api/                            # API Layer (Request/Response)
    ├── __init__.py
    └── schemas.py                  # Pydantic request/response DTOs
```

---

## 🏗️ Penjelasan Arsitektur & Kode

### Domain-Driven Design (DDD) Architecture

Project ini menggunakan **4-Layer Architecture** sesuai prinsip DDD:

```
┌─────────────────────────────────────────┐
│         API Layer (Presentation)        │  ← FastAPI endpoints, request/response
├─────────────────────────────────────────┤
│      Application Layer (Use Cases)      │  ← Business services & orchestration
├─────────────────────────────────────────┤
│       Domain Layer (Business Logic)     │  ← Entities, Value Objects, Rules
├─────────────────────────────────────────┤
│    Infrastructure Layer (Persistence)   │  ← Repositories, Database
└─────────────────────────────────────────┘
```

---

### 📦 Layer 1: Domain Layer (`domain/`)

**Inti dari business logic**, tidak bergantung pada layer lain.

#### `domain/entities.py` - Aggregate Roots
Berisi 3 aggregate utama dengan business rules:

**1. Reservation Aggregate**
```python
class Reservation:
    - reservation_id: UUID
    - confirmation_code: str (8 chars)
    - guest_id: UUID
    - room_type_id: str
    - date_range: DateRange
    - guest_count: GuestCount
    - total_amount: Money
    - status: ReservationStatus
    - special_requests: List[SpecialRequest]
    
    # Business Methods:
    - modify_dates()           # Ubah check-in/out
    - add_special_request()    # Tambah permintaan khusus
    - confirm()                # Konfirmasi setelah payment
    - check_in()               # Check-in guest
    - check_out()              # Check-out & hitung total
    - cancel()                 # Cancel dengan refund policy
    - mark_no_show()           # Tandai tidak datang
```

**2. Availability Aggregate**
```python
class Availability:
    - room_type_id: str
    - availability_date: date
    - total_rooms: int
    - reserved_rooms: int
    - blocked_rooms: int
    - overbooking_threshold: int
    
    # Business Methods:
    - reserve_rooms()          # Reserve kamar
    - release_rooms()          # Release kamar
    - block_rooms()            # Block untuk maintenance
    - unblock_rooms()          # Unblock setelah maintenance
    - can_accommodate()        # Cek apakah bisa accommodate
```

**3. WaitlistEntry Aggregate**
```python
class WaitlistEntry:
    - waitlist_id: UUID
    - guest_id: UUID
    - room_type_id: str
    - requested_dates: DateRange
    - guest_count: GuestCount
    - priority: Priority (1-4)
    - status: WaitlistStatus
    - expires_at: datetime
    
    # Business Methods:
    - convert_to_reservation() # Convert ke reservasi
    - expire()                 # Mark sebagai expired
    - extend_expiry()          # Perpanjang waktu
    - upgrade_priority()       # Naikkan prioritas
    - mark_notified()          # Tandai sudah notifikasi
    - calculate_priority_score() # Hitung score prioritas
```

#### `domain/value_objects.py` - Immutable Value Objects
Value objects yang tidak punya identity, hanya value:

```python
# DateRange - Validasi check-in/out
class DateRange:
    - check_in: date
    - check_out: date
    - Validasi: check_out > check_in
    - Method: nights() → hitung jumlah malam

# Money - Representasi uang
class Money:
    - amount: Decimal
    - currency: str (default "IDR")
    - Method: add(), subtract(), multiply()

# GuestCount - Jumlah tamu
class GuestCount:
    - adults: int (min 1)
    - children: int (min 0)
    - Method: total_guests()

# CancellationPolicy - Kebijakan cancel
class CancellationPolicy:
    - Method: calculate_refund() → 100%, 50%, atau 0%
    - Berdasarkan days_before_checkin

# SpecialRequest - Permintaan khusus
class SpecialRequest:
    - request_id: UUID
    - request_type: RequestType (enum)
    - description: str
    - fulfilled: bool
```

#### `domain/enums.py` - Business Enums
Semua enum untuk business rules:

```python
ReservationStatus:  PENDING → CONFIRMED → CHECKED_IN → CHECKED_OUT
                                       ↓
                                   CANCELLED / NO_SHOW

ReservationSource:  WEBSITE, MOBILE_APP, PHONE, OTA, DIRECT, CORPORATE

RequestType:        EARLY_CHECK_IN, LATE_CHECK_OUT, HIGH_FLOOR, 
                    ACCESSIBLE_ROOM, QUIET_ROOM, CRIBS, EXTRA_BED, 
                    SPECIAL_AMENITIES

WaitlistStatus:     ACTIVE → CONVERTED / EXPIRED / CANCELLED

Priority:           LOW=1, MEDIUM=2, HIGH=3, URGENT=4
```

#### `domain/repositories.py` - Repository Interfaces
Abstract interfaces (contract) untuk data access:

```python
class ReservationRepository(ABC):
    @abstractmethod
    async def save(reservation: Reservation) → None
    async def find_by_id(reservation_id: UUID) → Optional[Reservation]
    async def find_by_confirmation_code(code: str) → Optional[Reservation]
    async def find_by_guest(guest_id: UUID) → List[Reservation]
    async def find_all() → List[Reservation]

# Similar untuk AvailabilityRepository dan WaitlistRepository
```

#### `domain/events.py` - Domain Events
Events yang terjadi saat business action:

```python
ReservationCreated
ReservationConfirmed
ReservationCancelled
GuestCheckedIn
GuestCheckedOut
WaitlistEntryCreated
WaitlistEntryConverted
```

---

### 🎯 Layer 2: Application Layer (`application/`)

**Orchestrates business logic**, koordinasi antar aggregates.

#### `application/services.py` - Business Services

**1. ReservationService**
```python
class ReservationService:
    # Use Cases:
    - create_reservation()      # Buat reservasi + reserve availability
    - modify_reservation()      # Ubah reservasi + update availability
    - confirm_reservation()     # Konfirmasi payment
    - check_in_guest()          # Check-in + assign room
    - check_out_guest()         # Check-out + release availability
    - cancel_reservation()      # Cancel + release + refund
    - mark_no_show()            # No-show + release availability
    - add_special_request()     # Tambah special request
    
    # Koordinasi dengan:
    - ReservationRepository
    - AvailabilityRepository
    - WaitlistRepository (untuk auto-convert)
```

**2. AvailabilityService**
```python
class AvailabilityService:
    # Use Cases:
    - create_availability()     # Setup availability untuk room type
    - check_availability()      # Cek apakah available
    - reserve_rooms()           # Reserve untuk date range
    - release_rooms()           # Release setelah cancel
    - block_rooms()             # Block untuk maintenance
    - unblock_rooms()           # Unblock setelah selesai
    
    # Koordinasi dengan:
    - AvailabilityRepository
```

**3. WaitlistService**
```python
class WaitlistService:
    # Use Cases:
    - add_to_waitlist()         # Tambah ke waitlist
    - convert_to_reservation()  # Convert ke reservasi
    - upgrade_priority()        # Naikkan prioritas
    - extend_expiry()           # Perpanjang expiry
    - expire_entry()            # Mark sebagai expired
    - mark_notified()           # Tandai sudah notif
    - get_entries_to_notify()   # Get yang perlu notif
    
    # Koordinasi dengan:
    - WaitlistRepository
```

---

### 🗄️ Layer 3: Infrastructure Layer (`infrastructure/`)

**Implementasi teknis** untuk persistence.

#### `infrastructure/repositories/in_memory_repositories.py`

Implementasi repository menggunakan **in-memory storage** (dictionary):

```python
class InMemoryReservationRepository(ReservationRepository):
    _reservations: Dict[UUID, Reservation] = {}
    
    # Implementasi semua method dari interface:
    async def save(reservation)
    async def find_by_id(reservation_id)
    async def find_by_confirmation_code(code)
    async def find_by_guest(guest_id)
    async def find_all()
    async def delete(reservation_id)

# Similar untuk:
- InMemoryAvailabilityRepository
- InMemoryWaitlistRepository
```

**Kenapa In-Memory?**
- ✅ Mudah untuk testing & development
- ✅ Tidak perlu setup database
- ✅ Fast performance
- ⚠️ Data hilang saat restart (untuk production perlu database real)

#### `infrastructure/security.py` - JWT Authentication

```python
# Password hashing dengan bcrypt
def verify_password(plain_password, hashed_password)
def get_password_hash(password)

# JWT token generation
def create_access_token(data: dict, expires_delta: timedelta)
def decode_access_token(token: str)

# Constants:
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

---

### 🌐 Layer 4: API Layer (`api/`)

**HTTP interface** menggunakan FastAPI.

#### `api/schemas.py` - Request/Response DTOs

Pydantic models untuk validasi input/output:

```python
# Request Schemas:
CreateReservationRequest:
    - guest_id: UUID
    - room_type_id: str
    - check_in: date
    - check_out: date
    - adults: int
    - children: int
    - reservation_source: ReservationSource
    - special_requests: List[SpecialRequestInput]

ModifyReservationRequest:
    - check_in: Optional[date]
    - check_out: Optional[date]
    - adults: Optional[int]
    - children: Optional[int]

# Response Schemas:
ReservationResponse:
    - reservation_id: UUID
    - confirmation_code: str
    - guest_id: UUID
    - room_type_id: str
    - check_in: date
    - check_out: date
    - total_amount: Decimal
    - status: str
    - special_requests: List[SpecialRequestResponse]
    
# Similar untuk Availability dan Waitlist
```

#### `api/dependencies.py` - Dependency Injection

```python
# User database (in-memory untuk demo)
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": bcrypt_hash("admin123"),
        "disabled": False
    }
}

# Dependencies:
async def get_current_user(token: str)
async def get_current_active_user(current_user: User)
```

#### `main.py` - FastAPI Application

**Entry point** aplikasi dengan semua endpoints:

```python
app = FastAPI(
    title="Hotel Reservation API",
    description="API untuk Reservation Context dengan DDD",
    version="1.0.0"
)

# Initialize repositories (Dependency Injection)
reservation_repo = InMemoryReservationRepository()
availability_repo = InMemoryAvailabilityRepository()
waitlist_repo = InMemoryWaitlistRepository()

# Service factories
def get_reservation_service() → ReservationService
def get_availability_service() → AvailabilityService
def get_waitlist_service() → WaitlistService

# Endpoints (33 total):
# - 2 Auth endpoints (/token, /users/me)
# - 6 Enum reference endpoints
# - 12 Reservation endpoints
# - 7 Availability endpoints
# - 11 Waitlist endpoints
# - 1 Health check endpoint
```

---

### 🔄 Request Flow Example

**Contoh: Create Reservation**

```
1. CLIENT (Postman)
   POST /api/reservations
   Body: { guest_id, room_type_id, check_in, check_out, ... }
   Header: Authorization: Bearer <token>
   
2. API LAYER (main.py)
   ↓ Validate JWT token (get_current_active_user)
   ↓ Parse & validate request (CreateReservationRequest schema)
   ↓ Inject ReservationService dependency
   
3. APPLICATION LAYER (services.py)
   ReservationService.create_reservation()
   ↓ Check availability via AvailabilityService
   ↓ Create Reservation entity (domain logic)
   ↓ Reserve rooms in AvailabilityRepository
   ↓ Save reservation in ReservationRepository
   ↓ Emit ReservationCreated event
   
4. DOMAIN LAYER (entities.py)
   Reservation.__init__()
   ↓ Validate DateRange (check_out > check_in)
   ↓ Validate GuestCount (adults >= 1)
   ↓ Generate confirmation_code
   ↓ Calculate total_amount
   ↓ Set status = PENDING
   
5. INFRASTRUCTURE LAYER (repositories.py)
   InMemoryReservationRepository.save()
   ↓ Store in _reservations dictionary
   
6. RESPONSE
   ← Return ReservationResponse (201 Created)
   ← Include reservation_id & confirmation_code
```

---

### 🔐 Authentication Flow

**JWT-based authentication** untuk semua protected endpoints:

```
1. LOGIN
   POST /token
   Body: username=admin&password=admin123
   ↓
   Response: { "access_token": "eyJhbG...", "token_type": "bearer" }

2. USE TOKEN
   GET /api/reservations
   Header: Authorization: Bearer eyJhbG...
   ↓
   Dependency: get_current_active_user()
   ↓ Decode JWT token
   ↓ Verify signature & expiration
   ↓ Get user from fake_users_db
   ↓
   If valid: proceed to endpoint
   If invalid: 401 Unauthorized
```

**Protected Endpoints:**
- ✅ Semua `/api/reservations/*`
- ✅ Semua `/api/availability/*`
- ✅ Semua `/api/waitlist/*`

**Public Endpoints:**
- 🔓 `/token` (login)
- 🔓 `/api/health`
- 🔓 `/api/enums/*` (enum reference)

---

### 📊 Data Flow & State Management

**Reservation Lifecycle:**
```
CREATE → PENDING
         ↓ confirm_reservation()
       CONFIRMED
         ↓ check_in_guest()
       CHECKED_IN
         ↓ check_out_guest()
       CHECKED_OUT

Alternative flows:
PENDING/CONFIRMED → cancel_reservation() → CANCELLED
CONFIRMED → mark_no_show() → NO_SHOW
```

**Availability Management:**
```
CREATE availability (total_rooms=10)
  ↓
RESERVE (reserved_rooms += 2)
  ↓ available_rooms = 10 - 2 = 8
BLOCK (blocked_rooms += 1)
  ↓ available_rooms = 10 - 2 - 1 = 7
RELEASE (reserved_rooms -= 1)
  ↓ available_rooms = 10 - 1 - 1 = 8
```

**Waitlist Priority Scoring:**
```python
priority_score = (
    priority.value * 1000 +        # Priority weight (1000-4000)
    days_waiting * 10 +            # Semakin lama semakin tinggi
    (100 if notified else 0)       # Bonus jika sudah notified
)
```

---

### 🧪 Testing Strategy

**1. Unit Tests** (domain layer):
```python
# test_entities.py
def test_reservation_creation()
def test_date_range_validation()
def test_cancellation_refund_policy()
```

**2. Integration Tests** (application layer):
```python
# test_services.py
def test_create_reservation_with_availability()
def test_cancel_reservation_releases_rooms()
```

**3. API Tests** (Postman):
```
# test_api.py
def test_create_reservation_endpoint()
def test_authentication_required()
def test_enum_validation()
```

---

## 🚀 Installation & Setup

### Step 1: Clone/Navigate to Project
```bash
cd "c:\Users\Asus\Desktop\B Kenzie\ITB JR\SEMESTER 5\TST\TST TUBES MILESTONE 4"
```

### Step 2: Verify Python Installation
```bash
python --version
# Output: Python 3.x.x
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Atau manual:
```bash
pip install fastapi>=0.104.1 uvicorn>=0.24.0 pydantic>=2.5.0
```

### Step 4: Verify Installation
```bash
pip list | grep -E "fastapi|uvicorn|pydantic"
```

---

## ▶️ Running the Server

### Method 1: Direct Run (Recommended)
```bash
python main.py
```

Expected Output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Method 2: Using Uvicorn with Custom Port
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Method 3: Using Uvicorn with Different Port (if 8000 in use)
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Verify Server is Running
Open browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

---

## 🧪 Testing with Postman

### Import Collection

1. **Open Postman**
2. **Click** `File` → `Import`
3. **Select** `POSTMAN_COLLECTION.json` file
4. **Click** `Import`

### Collection Structure

Collection mencakup 4 folders:
1. **RESERVATIONS (12 endpoints)**
2. **AVAILABILITY (7 endpoints)**
3. **WAITLIST (11 endpoints)**
4. **ENUM REFERENCE (6 endpoints)**

### Running Tests: Complete Flow

#### **Phase 1: Setup Availability**
1. Create Availability (POST `/api/availabilities`)
   - Sets up room availability for testing

#### **Phase 2: Reservation Workflow**
1. Create Reservation (POST `/api/reservations`)
   - Saves `{{reservation_id}}` and `{{confirmation_code}}`
2. Get Reservation by ID (GET `/api/reservations/{{reservation_id}}`)
3. Modify Reservation (PUT `/api/reservations/{{reservation_id}}`)
4. Confirm Reservation (POST `/api/reservations/{{reservation_id}}/confirm`)
5. Check-in Guest (POST `/api/reservations/{{reservation_id}}/check-in`)
6. Check-out Guest (POST `/api/reservations/{{reservation_id}}/check-out`)

#### **Phase 3: Waitlist Workflow** (Optional)
1. Add to Waitlist (POST `/api/waitlist`)
   - Saves `{{waitlist_id}}`
2. Get Room Waitlist (GET `/api/waitlist/room/{room_type_id}`)
3. Convert to Reservation (POST `/api/waitlist/{{waitlist_id}}/convert`)
4. Upgrade Priority (POST `/api/waitlist/{{waitlist_id}}/upgrade-priority`)

#### **Phase 4: Enum Reference** (Optional)
1. Health Check (GET `/api/health`)
2. ReservationStatus (GET `/api/enums/reservation-status`)
3. BookingSource (GET `/api/enums/booking-source`)
4. RequestType (GET `/api/enums/request-type`)
5. WaitlistStatus (GET `/api/enums/waitlist-status`)
6. Priority (GET `/api/enums/priority`)

### Collection Variables

Postman collection menggunakan variables untuk chaining requests:

| Variable | Set By | Used In |
|----------|--------|---------|
| `{{reservation_id}}` | Create Reservation | Get, Modify, Confirm, Check-in, Check-out, Cancel |
| `{{confirmation_code}}` | Create Reservation | Get by Confirmation Code |
| `{{waitlist_id}}` | Add to Waitlist | Get, Convert, Expire, Upgrade Priority, Notify |

Variables otomatis tersimpan dengan test scripts yang sudah ada di collection.

### Tips Testing

✅ **Best Practices:**
- Test dalam urutan (jangan skip)
- Pastikan setiap request return status 2xx/3xx
- Check Response body untuk verify data
- Jika error, lihat error message di Response

⚠️ **Common Issues:**
- **Port already in use**: Jalankan server di port berbeda (`--port 8001`)
- **404 Not Found**: Pastikan server sudah berjalan (`http://localhost:8000/docs`)
- **Validation errors**: Check enum values dan format date (YYYY-MM-DD)
- **Variable not found**: Pastikan Create Reservation di-run terlebih dahulu

---

## 📡 API Endpoints

### Health & Reference
```
GET  /api/health
GET  /api/enums/reservation-status
GET  /api/enums/booking-source
GET  /api/enums/request-type
GET  /api/enums/waitlist-status
GET  /api/enums/priority
```

### Reservations (12 endpoints)
```
POST   /api/reservations                                 # Create
GET    /api/reservations                                 # Get all
GET    /api/reservations/{reservation_id}               # Get by ID
GET    /api/reservations/code/{confirmation_code}       # Get by code
GET    /api/reservations/guest/{guest_id}               # Get by guest
PUT    /api/reservations/{reservation_id}               # Modify
POST   /api/reservations/{reservation_id}/confirm       # Confirm
POST   /api/reservations/{reservation_id}/check-in      # Check-in
POST   /api/reservations/{reservation_id}/check-out     # Check-out
POST   /api/reservations/{reservation_id}/cancel        # Cancel
POST   /api/reservations/{reservation_id}/no-show       # Mark no-show
POST   /api/reservations/{reservation_id}/special-request # Add special request
```

### Availability (7 endpoints)
```
POST   /api/availabilities                               # Create
GET    /api/availabilities/{room_type_id}/{date}        # Get
POST   /api/availabilities/check                        # Check availability
POST   /api/availabilities/reserve                      # Reserve rooms
POST   /api/availabilities/release                      # Release rooms
POST   /api/availabilities/block                        # Block rooms
POST   /api/availabilities/unblock                      # Unblock rooms
```

### Waitlist (11 endpoints)
```
POST   /api/waitlist                                    # Add to waitlist
GET    /api/waitlist                                    # Get all active
GET    /api/waitlist/{waitlist_id}                     # Get by ID
GET    /api/waitlist/guest/{guest_id}                  # Get by guest
GET    /api/waitlist/room/{room_type_id}               # Get by room type
GET    /api/waitlist/active                            # Get active entries
POST   /api/waitlist/{waitlist_id}/convert             # Convert to reservation
POST   /api/waitlist/{waitlist_id}/expire              # Mark as expired
POST   /api/waitlist/{waitlist_id}/extend-expiry       # Extend expiry
POST   /api/waitlist/{waitlist_id}/upgrade-priority    # Upgrade priority
POST   /api/waitlist/{waitlist_id}/notify              # Mark notified
GET    /api/waitlist/notify/pending                    # Get to notify
```

---

## 📚 Enum Reference

### ReservationStatus
```
PENDING → CONFIRMED → CHECKED_IN → CHECKED_OUT
                   ↓
                 CANCELLED / NO_SHOW
```
Values: `PENDING`, `CONFIRMED`, `CHECKED_IN`, `CHECKED_OUT`, `CANCELLED`, `NO_SHOW`

### BookingSource
Values: `WEBSITE`, `MOBILE_APP`, `PHONE`, `OTA`, `DIRECT`, `CORPORATE`

### RequestType
Values: `EARLY_CHECK_IN`, `LATE_CHECK_OUT`, `HIGH_FLOOR`, `ACCESSIBLE_ROOM`, `QUIET_ROOM`, `CRIBS`, `EXTRA_BED`, `SPECIAL_AMENITIES`

### WaitlistStatus
```
ACTIVE → CONVERTED / EXPIRED / CANCELLED
```
Values: `ACTIVE`, `CONVERTED`, `EXPIRED`, `CANCELLED`

### Priority
```
1 = LOW
2 = MEDIUM
3 = HIGH
4 = URGENT
```

---

## 🐛 Troubleshooting

### Error: Port 8000 already in use
```bash
# Solution 1: Kill existing process
powershell -Command "Get-Process -Port 8000 | Stop-Process -Force"

# Solution 2: Use different port
python main.py --port 8001
```

### Error: Module not found (domain, api, etc)
```bash
# Make sure you're in correct directory:
cd "c:\Users\Asus\Desktop\B Kenzie\ITB JR\SEMESTER 5\TST\TST TUBES MILESTONE 4"

# Reinstall dependencies:
pip install -r requirements.txt
```

### Error: Enum validation failed ('WEBSITE' is not valid)
```
✅ This is FIXED in current version
Ensure you have latest code with enum imports in main.py
Restart server with: python main.py
```

### Error: 404 Not Found on enum endpoints
```
✅ This is FIXED in current version
Enum reference endpoints added:
- /api/health
- /api/enums/reservation-status
- /api/enums/booking-source
- /api/enums/request-type
- /api/enums/waitlist-status
- /api/enums/priority
```

### Postman shows old cached response
```bash
# Clear Postman cache:
1. Settings (⚙️) → Data → Clear
2. Close Postman completely
3. Reopen Postman
4. Re-import collection
```

### Variable not found in request
```
Make sure to run requests in order:
1. Create Reservation (saves {{reservation_id}})
2. Then use {{reservation_id}} in subsequent requests

Don't skip Create step!
```

---

## 📝 Request/Response Examples

### Create Reservation Request
```json
{
  "guest_id": "123e4567-e89b-12d3-a456-426614174000",
  "room_type_id": "DELUXE_001",
  "check_in": "2025-11-20",
  "check_out": "2025-11-22",
  "adults": 2,
  "children": 1,
  "booking_source": "WEBSITE",
  "special_requests": [
    {
      "type": "EARLY_CHECK_IN",
      "description": "Early check-in needed"
    }
  ],
  "created_by": "TEST_USER"
}
```

### Create Reservation Response (201 Created)
```json
{
  "reservation_id": "da12dc3f-b6df-4b96-86a3-82c77c77ba87",
  "confirmation_code": "WL7G8L43",
  "guest_id": "123e4567-e89b-12d3-a456-426614174000",
  "room_type_id": "DELUXE_001",
  "check_in": "2025-11-20",
  "check_out": "2025-11-22",
  "adults": 2,
  "children": 1,
  "total_amount": "2000000",
  "currency": "IDR",
  "status": "PENDING",
  "booking_source": "WEBSITE",
  "special_requests": [
    {
      "request_id": "212c9274-cff0-4d6a-b55d-426ca5358a33",
      "request_type": "EARLY_CHECK_IN",
      "description": "Early check-in needed",
      "fulfilled": false,
      "created_at": "2025-11-17T05:20:26.215982"
    }
  ],
  "created_at": "2025-11-17T05:20:26.215936",
  "modified_at": "2025-11-17T05:20:26.215991",
  "created_by": "TEST_USER",
  "version": 2
}
```

### Add to Waitlist Request
```json
{
  "guest_id": "223e4567-e89b-12d3-a456-426614174000",
  "room_type_id": "DELUXE_001",
  "check_in": "2025-11-25",
  "check_out": "2025-11-27",
  "adults": 2,
  "children": 0,
  "priority": "2"
}
```

---

## 📖 Additional Resources

### API Documentation (Auto-generated)
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Domain-Driven Design Concepts
- **Aggregates**: Reservation, Availability, WaitlistEntry
- **Value Objects**: DateRange, Money, GuestCount, CancellationPolicy
- **Repositories**: Abstract interfaces with in-memory implementations
- **Services**: Business logic layer coordinating domain operations

### Project Files
- `domain/entities.py` - Aggregate definitions and business rules
- `domain/value_objects.py` - Immutable value objects
- `domain/enums.py` - All enum definitions
- `application/services.py` - Use case implementations
- `api/schemas.py` - Request/Response validation
- `infrastructure/repositories/in_memory_repositories.py` - Data persistence

---

## ✅ Verification Checklist

Before submitting, verify:

- [x] Server starts without errors: `python main.py`
- [x] Health check works: `http://localhost:8000/api/health`
- [x] Swagger UI loads: `http://localhost:8000/docs`
- [x] All 33 endpoints visible in Swagger
- [x] Postman collection imports successfully
- [x] Create Reservation (POST) returns 201
- [x] Enum validation works (WEBSITE, PHONE, etc)
- [x] Variables save/chain properly in Postman
- [x] All enum reference endpoints return 200

---

