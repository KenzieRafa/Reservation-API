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
TST TUBES MILESTONE 4 - Copy/
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

## 🚀 Installation & Setup

### Step 1: Clone/Navigate to Project
```bash
cd "c:\Users\Asus\Desktop\B Kenzie\ITB JR\SEMESTER 5\TST\TST TUBES MILESTONE 4 - Copy"
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
cd "c:\Users\Asus\Desktop\B Kenzie\ITB JR\SEMESTER 5\TST\TST TUBES MILESTONE 4 - Copy"

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

## 👨‍💻 Author
Domain-Driven Design Implementation for Hotel Reservation System
Created with ❤️ using FastAPI + Pydantic

---

## 📄 License
This project is for educational purposes.

---

**Last Updated**: November 17, 2025
**Version**: 1.0.0 Complete
