# 📋 Panduan Payload API - Hotel Reservation System

Dokumentasi lengkap untuk testing API menggunakan Postman.

## 🔐 Authentication

### 1. Login (Dapatkan Token Terlebih Dahulu)
**Endpoint:** `POST http://localhost:8000/token`  
**Content-Type:** `application/x-www-form-urlencoded`

**Body (x-www-form-urlencoded):**
```
username: admin
password: admin123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

> ⚠️ **PENTING:** Setelah login, copy `access_token` dan set di Authorization → Bearer Token untuk semua endpoint lainnya!

---

## 🏨 RESERVATIONS (12 Endpoints)

### 1. Create Reservation
**Endpoint:** `POST http://localhost:8000/api/reservations`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "guest_id": "123e4567-e89b-12d3-a456-426614174000",
  "room_type_id": "DELUXE_001",
  "check_in": "2025-12-10",
  "check_out": "2025-12-12",
  "adults": 2,
  "children": 1,
  "reservation_source": "WEBSITE",
  "special_requests": [
    {
      "type": "EARLY_CHECK_IN",
      "description": "Early check-in at 12:00 PM"
    }
  ],
  "created_by": "TEST_USER"
}
```

**Response:** Simpan `reservation_id` dan `confirmation_code` untuk endpoint berikutnya!

---

### 2. Get All Reservations
**Endpoint:** `GET http://localhost:8000/api/reservations`  
**Authorization:** Bearer Token Required

**Payload:** Tidak ada (GET request)

---

### 3. Get Reservation by ID
**Endpoint:** `GET http://localhost:8000/api/reservations/{reservation_id}`  
**Authorization:** Bearer Token Required

**Contoh:**
```
GET http://localhost:8000/api/reservations/123e4567-e89b-12d3-a456-426614174000
```

---

### 4. Get by Confirmation Code
**Endpoint:** `GET http://localhost:8000/api/reservations/code/{confirmation_code}`  
**Authorization:** Bearer Token Required

**Contoh:**
```
GET http://localhost:8000/api/reservations/code/ABC123XYZ
```

---

### 5. Get Guest Reservations
**Endpoint:** `GET http://localhost:8000/api/reservations/guest/{guest_id}`  
**Authorization:** Bearer Token Required

**Contoh:**
```
GET http://localhost:8000/api/reservations/guest/123e4567-e89b-12d3-a456-426614174000
```

---

### 6. Modify Reservation
**Endpoint:** `PUT http://localhost:8000/api/reservations/{reservation_id}`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "check_out": "2025-12-15"
}
```

**Payload Lengkap (Opsional):**
```json
{
  "check_in": "2025-12-10",
  "check_out": "2025-12-15",
  "adults": 3,
  "children": 2,
  "room_type_id": "SUITE_001"
}
```

---

### 7. Add Special Request
**Endpoint:** `POST http://localhost:8000/api/reservations/{reservation_id}/special-requests`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "request_type": "EXTRA_BED",
  "description": "Need one extra bed for child"
}
```

**Request Types yang Valid:**
- `EARLY_CHECK_IN`
- `LATE_CHECK_OUT`
- `HIGH_FLOOR`
- `ACCESSIBLE_ROOM`
- `QUIET_ROOM`
- `CRIBS`
- `EXTRA_BED`
- `SPECIAL_AMENITIES`

---

### 8. Confirm Reservation
**Endpoint:** `POST http://localhost:8000/api/reservations/{reservation_id}/confirm`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "payment_confirmed": true
}
```

---

### 9. Check-In Guest
**Endpoint:** `POST http://localhost:8000/api/reservations/{reservation_id}/check-in`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "room_number": "301"
}
```

---

### 10. Check-Out Guest
**Endpoint:** `POST http://localhost:8000/api/reservations/{reservation_id}/check-out`  
**Authorization:** Bearer Token Required

**Payload:** Tidak ada (POST tanpa body)

**Response:**
```json
{
  "amount": 1500000.00,
  "currency": "IDR"
}
```

---

### 11. Cancel Reservation
**Endpoint:** `POST http://localhost:8000/api/reservations/{reservation_id}/cancel`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "reason": "Changed travel plans"
}
```

**Response:**
```json
{
  "amount": 750000.00,
  "currency": "IDR"
}
```

---

### 12. Mark No-Show
**Endpoint:** `POST http://localhost:8000/api/reservations/{reservation_id}/no-show`  
**Authorization:** Bearer Token Required

**Payload:** Tidak ada (POST tanpa body)

---

## 📅 AVAILABILITY (7 Endpoints)

### 1. Create Availability
**Endpoint:** `POST http://localhost:8000/api/availability`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "room_type_id": "DELUXE_001",
  "availability_date": "2025-12-10",
  "total_rooms": 10,
  "overbooking_threshold": 2
}
```

---

### 2. Get Availability
**Endpoint:** `GET http://localhost:8000/api/availability/{room_type_id}/{date}`  
**Authorization:** Bearer Token Required

**Contoh:**
```
GET http://localhost:8000/api/availability/DELUXE_001/2025-12-10
```

---

### 3. Check Availability
**Endpoint:** `POST http://localhost:8000/api/availability/check`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "room_type_id": "DELUXE_001",
  "start_date": "2025-12-10",
  "end_date": "2025-12-12",
  "required_count": 2
}
```

**Response:**
```json
{
  "available": true
}
```

---

### 4. Reserve Rooms
**Endpoint:** `POST http://localhost:8000/api/availability/reserve`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "room_type_id": "DELUXE_001",
  "start_date": "2025-12-10",
  "end_date": "2025-12-12",
  "count": 2
}
```

---

### 5. Release Rooms
**Endpoint:** `POST http://localhost:8000/api/availability/release`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "room_type_id": "DELUXE_001",
  "start_date": "2025-12-10",
  "end_date": "2025-12-12",
  "count": 1
}
```

---

### 6. Block Rooms
**Endpoint:** `POST http://localhost:8000/api/availability/block`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "room_type_id": "DELUXE_001",
  "start_date": "2025-12-10",
  "end_date": "2025-12-12",
  "count": 1,
  "reason": "Maintenance - AC repair"
}
```

---

### 7. Unblock Rooms
**Endpoint:** `POST http://localhost:8000/api/availability/unblock`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "room_type_id": "DELUXE_001",
  "start_date": "2025-12-10",
  "end_date": "2025-12-12",
  "count": 1
}
```

---

## 📝 WAITLIST (11 Endpoints)

### 1. Add to Waitlist
**Endpoint:** `POST http://localhost:8000/api/waitlist`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "guest_id": "223e4567-e89b-12d3-a456-426614174000",
  "room_type_id": "DELUXE_001",
  "check_in": "2025-12-15",
  "check_out": "2025-12-17",
  "adults": 2,
  "children": 0,
  "priority": "2"
}
```

**Priority Values:**
- `"1"` = LOW
- `"2"` = MEDIUM
- `"3"` = HIGH
- `"4"` = URGENT

**Response:** Simpan `waitlist_id` untuk endpoint berikutnya!

---

### 2. Get All Active Waitlist
**Endpoint:** `GET http://localhost:8000/api/waitlist/active`  
**Authorization:** Bearer Token Required

**Payload:** Tidak ada (GET request)

---

### 3. Get Guest Waitlist
**Endpoint:** `GET http://localhost:8000/api/waitlist/guest/{guest_id}`  
**Authorization:** Bearer Token Required

**Contoh:**
```
GET http://localhost:8000/api/waitlist/guest/223e4567-e89b-12d3-a456-426614174000
```

---

### 4. Get Room Waitlist (by Priority)
**Endpoint:** `GET http://localhost:8000/api/waitlist/room/{room_type_id}`  
**Authorization:** Bearer Token Required

**Contoh:**
```
GET http://localhost:8000/api/waitlist/room/DELUXE_001
```

---

### 5. Get Waitlist Entry by ID
**Endpoint:** `GET http://localhost:8000/api/waitlist/{waitlist_id}`  
**Authorization:** Bearer Token Required

**Contoh:**
```
GET http://localhost:8000/api/waitlist/123e4567-e89b-12d3-a456-426614174000
```

---

### 6. Convert to Reservation
**Endpoint:** `POST http://localhost:8000/api/waitlist/{waitlist_id}/convert`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "reservation_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

### 7. Mark as Notified
**Endpoint:** `POST http://localhost:8000/api/waitlist/{waitlist_id}/notify`  
**Authorization:** Bearer Token Required

**Payload:** Tidak ada (POST tanpa body)

---

### 8. Upgrade Priority
**Endpoint:** `POST http://localhost:8000/api/waitlist/{waitlist_id}/upgrade-priority`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "new_priority": "3"
}
```

---

### 9. Extend Expiry
**Endpoint:** `POST http://localhost:8000/api/waitlist/{waitlist_id}/extend`  
**Authorization:** Bearer Token Required

**Payload:**
```json
{
  "additional_days": 7
}
```

---

### 10. Expire Entry
**Endpoint:** `POST http://localhost:8000/api/waitlist/{waitlist_id}/expire`  
**Authorization:** Bearer Token Required

**Payload:** Tidak ada (POST tanpa body)

---

### 11. Get Entries Pending Notification
**Endpoint:** `GET http://localhost:8000/api/waitlist/notify/pending`  
**Authorization:** Bearer Token Required

**Payload:** Tidak ada (GET request)

---

## 📚 ENUM REFERENCE

### Reservation Source
```
WEBSITE
MOBILE_APP
PHONE
OTA
DIRECT
CORPORATE
```

### Request Type
```
EARLY_CHECK_IN
LATE_CHECK_OUT
HIGH_FLOOR
ACCESSIBLE_ROOM
QUIET_ROOM
CRIBS
EXTRA_BED
SPECIAL_AMENITIES
```

### Reservation Status
```
PENDING
CONFIRMED
CHECKED_IN
CHECKED_OUT
CANCELLED
NO_SHOW
```

### Waitlist Status
```
ACTIVE
CONVERTED
EXPIRED
CANCELLED
```

### Priority (Waitlist)
```
1 = LOW
2 = MEDIUM
3 = HIGH
4 = URGENT
```

---

## 🚀 Quick Start Guide

### Step 1: Import Collection
1. Buka Postman
2. Import file `POSTMAN_COLLECTION.json`
3. Collection akan otomatis ter-setup dengan semua endpoint

### Step 2: Login
1. Buka folder "AUTH (Login First)"
2. Jalankan request "Login (Get Token)"
3. Token akan otomatis tersimpan di collection variables

### Step 3: Test Endpoints
1. Pilih endpoint yang ingin di-test
2. Authorization sudah otomatis menggunakan token dari login
3. Copy-paste payload dari guide ini
4. Klik "Send"

---

## 💡 Tips Testing

### 1. Urutan Testing yang Disarankan
```
1. Login → Get Token
2. Create Availability → Setup room availability
3. Create Reservation → Buat reservasi baru
4. Confirm Reservation → Konfirmasi pembayaran
5. Check-In Guest → Check-in tamu
6. Check-Out Guest → Check-out tamu
```

### 2. Testing Waitlist Flow
```
1. Login → Get Token
2. Add to Waitlist → Tambah ke waitlist
3. Get Active Waitlist → Lihat semua waitlist aktif
4. Upgrade Priority → Naikkan prioritas
5. Convert to Reservation → Convert ke reservasi
```

### 3. Menyimpan Variables
Postman collection sudah di-setup untuk auto-save:
- `access_token` → Dari login
- `reservation_id` → Dari create reservation
- `confirmation_code` → Dari create reservation
- `waitlist_id` → Dari add to waitlist

Gunakan `{{variable_name}}` di URL atau body untuk menggunakan variable ini.

---

## ❌ Common Errors & Solutions

### Error 401: Unauthorized
**Penyebab:** Token tidak valid atau expired  
**Solusi:** Login ulang untuk mendapatkan token baru

### Error 400: Bad Request
**Penyebab:** Format payload salah atau data tidak valid  
**Solusi:** 
- Cek format JSON (harus valid)
- Pastikan enum values benar (case-sensitive)
- Pastikan tanggal format: `YYYY-MM-DD`

### Error 404: Not Found
**Penyebab:** ID tidak ditemukan  
**Solusi:** 
- Pastikan sudah create resource terlebih dahulu
- Gunakan ID yang valid dari response sebelumnya

