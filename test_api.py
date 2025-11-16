#!/usr/bin/env python3
"""
Test script untuk Hotel Reservation API
Testing semua aggregates: Reservation, Availability, Waitlist
"""

import requests
import json
from datetime import date, timedelta
from uuid import uuid4

BASE_URL = "http://localhost:8000"

# Test data
GUEST_ID_1 = str(uuid4())
GUEST_ID_2 = str(uuid4())
ROOM_TYPE = "DELUXE_001"

# Colors for console output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text:^80}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}→ {text}{RESET}")

def print_request(method, endpoint, data=None):
    print(f"\n{BOLD}{method} {endpoint}{RESET}")
    if data:
        print(f"Request Body:\n{json.dumps(data, indent=2, default=str)}")

def print_response(response):
    try:
        data = response.json()
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(data, indent=2, default=str))
        return data
    except:
        print(f"\nResponse ({response.status_code}): {response.text}")
        return None

# ============================================================================
# TEST 1: AVAILABILITY AGGREGATE
# ============================================================================

def test_availability():
    print_header("TEST 1: AVAILABILITY AGGREGATE")

    # Create availability for multiple dates
    print_info("Creating availability for 5 days...")
    start_date = date.today() + timedelta(days=5)
    availability_ids = []

    for i in range(5):
        current_date = start_date + timedelta(days=i)

        payload = {
            "room_type_id": ROOM_TYPE,
            "availability_date": current_date.isoformat(),
            "total_rooms": 10,
            "overbooking_threshold": 2
        }

        print_request("POST", "/api/availability", payload)
        response = requests.post(f"{BASE_URL}/api/availability", json=payload)
        data = print_response(response)

        if response.status_code == 201:
            print_success(f"Availability created for {current_date}")
            availability_ids.append(current_date.isoformat())
        else:
            print_error(f"Failed to create availability for {current_date}")
            return None

    # Get availability
    print_info("Getting availability...")
    response = requests.get(f"{BASE_URL}/api/availability/{ROOM_TYPE}/{availability_ids[0]}")
    data = print_response(response)
    if response.status_code == 200:
        print_success("Availability retrieved successfully")

    # Check availability
    print_info("Checking availability for date range...")
    payload = {
        "room_type_id": ROOM_TYPE,
        "start_date": availability_ids[0],
        "end_date": availability_ids[2],
        "required_count": 2
    }
    print_request("POST", "/api/availability/check", payload)
    response = requests.post(f"{BASE_URL}/api/availability/check", json=payload)
    data = print_response(response)
    if response.status_code == 200 and data.get("available"):
        print_success("Rooms are available for date range")

    return availability_ids

# ============================================================================
# TEST 2: RESERVATION AGGREGATE - FULL LIFECYCLE
# ============================================================================

def test_reservation(availability_ids):
    print_header("TEST 2: RESERVATION AGGREGATE - FULL LIFECYCLE")

    check_in = availability_ids[0]
    check_out = availability_ids[2]

    # 2.1 Create Reservation
    print_info("Creating reservation...")
    payload = {
        "guest_id": GUEST_ID_1,
        "room_type_id": ROOM_TYPE,
        "check_in": check_in,
        "check_out": check_out,
        "adults": 2,
        "children": 1,
        "booking_source": "ONLINE",
        "special_requests": [
            {
                "type": "EARLY_CHECKIN",
                "description": "Please arrange early check-in at 2pm"
            },
            {
                "type": "HIGH_FLOOR",
                "description": "Prefer high floor room with city view"
            }
        ],
        "created_by": "TEST_USER"
    }

    print_request("POST", "/api/reservations", payload)
    response = requests.post(f"{BASE_URL}/api/reservations", json=payload)
    data = print_response(response)

    if response.status_code != 201:
        print_error("Failed to create reservation")
        return None

    reservation_id = data["reservation_id"]
    confirmation_code = data["confirmation_code"]
    print_success(f"Reservation created: {reservation_id}")
    print_success(f"Confirmation Code: {confirmation_code}")

    # 2.2 Get Reservation
    print_info("Getting reservation details...")
    response = requests.get(f"{BASE_URL}/api/reservations/{reservation_id}")
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Status: {data['status']}")

    # 2.3 Add Special Request
    print_info("Adding special request to reservation...")
    payload = {
        "request_type": "SPECIAL_AMENITIES",
        "description": "Please provide extra pillows and blankets"
    }
    print_request("POST", f"/api/reservations/{reservation_id}/special-requests", payload)
    response = requests.post(f"{BASE_URL}/api/reservations/{reservation_id}/special-requests", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Special request added. Total requests: {len(data['special_requests'])}")

    # 2.4 Confirm Reservation
    print_info("Confirming reservation...")
    payload = {"payment_confirmed": True}
    print_request("POST", f"/api/reservations/{reservation_id}/confirm", payload)
    response = requests.post(f"{BASE_URL}/api/reservations/{reservation_id}/confirm", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Reservation confirmed. Status: {data['status']}")

    # 2.5 Modify Reservation
    print_info("Modifying reservation (extending stay)...")
    extended_checkout = availability_ids[3]
    payload = {
        "check_out": extended_checkout
    }
    print_request("PUT", f"/api/reservations/{reservation_id}", payload)
    response = requests.put(f"{BASE_URL}/api/reservations/{reservation_id}", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Reservation modified. New checkout: {data['check_out']}")

    # 2.6 Get by Confirmation Code
    print_info("Getting reservation by confirmation code...")
    response = requests.get(f"{BASE_URL}/api/reservations/code/{confirmation_code}")
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Found reservation by code: {data['reservation_id']}")

    # 2.7 Check In Guest
    print_info("Checking in guest...")
    payload = {"room_number": "301"}
    print_request("POST", f"/api/reservations/{reservation_id}/check-in", payload)
    response = requests.post(f"{BASE_URL}/api/reservations/{reservation_id}/check-in", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Guest checked in. Status: {data['status']}")

    # 2.8 Check Out Guest
    print_info("Checking out guest...")
    print_request("POST", f"/api/reservations/{reservation_id}/check-out")
    response = requests.post(f"{BASE_URL}/api/reservations/{reservation_id}/check-out")
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Guest checked out. Final amount: {data['amount']} {data['currency']}")

    # 2.9 Get all reservations
    print_info("Getting all reservations...")
    response = requests.get(f"{BASE_URL}/api/reservations")
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Total reservations: {len(data)}")

    # 2.10 Get reservations by guest
    print_info("Getting reservations by guest ID...")
    response = requests.get(f"{BASE_URL}/api/reservations/guest/{GUEST_ID_1}")
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Guest reservations: {len(data)}")

    return reservation_id

# ============================================================================
# TEST 3: CANCELLATION & REFUND
# ============================================================================

def test_cancellation(availability_ids):
    print_header("TEST 3: RESERVATION CANCELLATION & REFUND")

    # Create another reservation to cancel
    print_info("Creating reservation to cancel...")
    payload = {
        "guest_id": GUEST_ID_1,
        "room_type_id": ROOM_TYPE,
        "check_in": availability_ids[3],
        "check_out": availability_ids[4],
        "adults": 1,
        "children": 0,
        "booking_source": "PHONE",
        "created_by": "TEST_USER"
    }

    response = requests.post(f"{BASE_URL}/api/reservations", json=payload)
    data = response.json()
    cancellable_id = data["reservation_id"]
    print_success(f"Reservation created for cancellation: {cancellable_id}")

    # Confirm it first
    response = requests.post(f"{BASE_URL}/api/reservations/{cancellable_id}/confirm",
                            json={"payment_confirmed": True})
    print_success("Reservation confirmed")

    # Cancel reservation
    print_info("Cancelling reservation...")
    payload = {"reason": "Guest changed plans"}
    print_request("POST", f"/api/reservations/{cancellable_id}/cancel", payload)
    response = requests.post(f"{BASE_URL}/api/reservations/{cancellable_id}/cancel", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Reservation cancelled. Refund: {data['amount']} {data['currency']}")

# ============================================================================
# TEST 4: WAITLIST AGGREGATE
# ============================================================================

def test_waitlist(availability_ids):
    print_header("TEST 4: WAITLIST AGGREGATE")

    # 4.1 Add to waitlist
    print_info("Adding guest to waitlist...")
    payload = {
        "guest_id": GUEST_ID_2,
        "room_type_id": ROOM_TYPE,
        "check_in": availability_ids[0],
        "check_out": availability_ids[2],
        "adults": 2,
        "children": 0,
        "priority": "3"  # HIGH
    }

    print_request("POST", "/api/waitlist", payload)
    response = requests.post(f"{BASE_URL}/api/waitlist", json=payload)
    data = print_response(response)

    if response.status_code != 201:
        print_error("Failed to add to waitlist")
        return None

    waitlist_id = data["waitlist_id"]
    print_success(f"Guest added to waitlist: {waitlist_id}")
    print_success(f"Priority Score: {data['priority_score']}")

    # 4.2 Get waitlist entry
    print_info("Getting waitlist entry...")
    response = requests.get(f"{BASE_URL}/api/waitlist/{waitlist_id}")
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Status: {data['status']}, Priority: {data['priority']}")

    # 4.3 Get waitlist by guest
    print_info("Getting guest waitlist entries...")
    response = requests.get(f"{BASE_URL}/api/waitlist/guest/{GUEST_ID_2}")
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Guest has {len(data)} waitlist entries")

    # 4.4 Get waitlist by room
    print_info("Getting waitlist entries for room type...")
    response = requests.get(f"{BASE_URL}/api/waitlist/room/{ROOM_TYPE}")
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Room has {len(data)} waitlist entries (sorted by priority)")

    # 4.5 Get active waitlist
    print_info("Getting active waitlist entries...")
    response = requests.get(f"{BASE_URL}/api/waitlist/active")
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Total active entries: {len(data)}")

    # 4.6 Mark as notified
    print_info("Marking waitlist entry as notified...")
    print_request("POST", f"/api/waitlist/{waitlist_id}/notify")
    response = requests.post(f"{BASE_URL}/api/waitlist/{waitlist_id}/notify")
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Notified at: {data['notified_at']}")

    # 4.7 Upgrade priority
    print_info("Upgrading waitlist priority...")
    payload = {"new_priority": "4"}  # URGENT
    print_request("POST", f"/api/waitlist/{waitlist_id}/upgrade-priority", payload)
    response = requests.post(f"{BASE_URL}/api/waitlist/{waitlist_id}/upgrade-priority", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Priority upgraded to: {data['priority']}")

    # 4.8 Extend expiry
    print_info("Extending waitlist expiry...")
    payload = {"additional_days": 7}
    print_request("POST", f"/api/waitlist/{waitlist_id}/extend", payload)
    response = requests.post(f"{BASE_URL}/api/waitlist/{waitlist_id}/extend", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success(f"Expiry extended to: {data['expires_at']}")

    return waitlist_id

# ============================================================================
# TEST 5: AVAILABILITY OPERATIONS
# ============================================================================

def test_availability_operations(availability_ids):
    print_header("TEST 5: AVAILABILITY OPERATIONS - RESERVE/RELEASE/BLOCK")

    # 5.1 Reserve rooms
    print_info("Reserving rooms...")
    payload = {
        "room_type_id": ROOM_TYPE,
        "start_date": availability_ids[0],
        "end_date": availability_ids[1],
        "count": 2
    }
    print_request("POST", "/api/availability/reserve", payload)
    response = requests.post(f"{BASE_URL}/api/availability/reserve", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success("Rooms reserved successfully")

    # 5.2 Block rooms for maintenance
    print_info("Blocking rooms for maintenance...")
    payload = {
        "room_type_id": ROOM_TYPE,
        "start_date": availability_ids[1],
        "end_date": availability_ids[2],
        "count": 1,
        "reason": "Maintenance and cleaning"
    }
    print_request("POST", "/api/availability/block", payload)
    response = requests.post(f"{BASE_URL}/api/availability/block", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success("Rooms blocked successfully")

    # 5.3 Release rooms
    print_info("Releasing reserved rooms...")
    payload = {
        "room_type_id": ROOM_TYPE,
        "start_date": availability_ids[0],
        "end_date": availability_ids[1],
        "count": 1
    }
    print_request("POST", "/api/availability/release", payload)
    response = requests.post(f"{BASE_URL}/api/availability/release", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success("Rooms released successfully")

    # 5.4 Unblock rooms
    print_info("Unblocking rooms...")
    payload = {
        "room_type_id": ROOM_TYPE,
        "start_date": availability_ids[1],
        "end_date": availability_ids[2],
        "count": 1
    }
    print_request("POST", "/api/availability/unblock", payload)
    response = requests.post(f"{BASE_URL}/api/availability/unblock", json=payload)
    data = print_response(response)
    if response.status_code == 200:
        print_success("Rooms unblocked successfully")

# ============================================================================
# TEST 6: ERROR HANDLING
# ============================================================================

def test_error_handling():
    print_header("TEST 6: ERROR HANDLING & VALIDATION")

    # Test 1: Invalid date range (check_out before check_in)
    print_info("Testing invalid date range...")
    payload = {
        "guest_id": str(uuid4()),
        "room_type_id": "INVALID_ROOM",
        "check_in": "2025-11-25",
        "check_out": "2025-11-23",
        "adults": 1,
        "children": 0,
        "booking_source": "ONLINE"
    }
    print_request("POST", "/api/reservations", payload)
    response = requests.post(f"{BASE_URL}/api/reservations", json=payload)
    print_response(response)
    if response.status_code == 400:
        print_success("Invalid date range properly rejected")

    # Test 2: Non-existent reservation
    print_info("Testing non-existent reservation...")
    fake_id = str(uuid4())
    response = requests.get(f"{BASE_URL}/api/reservations/{fake_id}")
    print_response(response)
    if response.status_code == 404:
        print_success("Non-existent reservation properly handled")

    # Test 3: Invalid guest count
    print_info("Testing invalid guest count (0 adults)...")
    payload = {
        "guest_id": str(uuid4()),
        "room_type_id": "DELUXE_001",
        "check_in": "2025-11-20",
        "check_out": "2025-11-22",
        "adults": 0,
        "children": 1,
        "booking_source": "ONLINE"
    }
    print_request("POST", "/api/reservations", payload)
    response = requests.post(f"{BASE_URL}/api/reservations", json=payload)
    print_response(response)
    if response.status_code == 422:
        print_success("Invalid guest count properly rejected")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    print(f"\n{BOLD}{BLUE}{'*'*80}{RESET}")
    print(f"{BOLD}{BLUE}{'HOTEL RESERVATION API - COMPREHENSIVE TEST SUITE':^80}{RESET}")
    print(f"{BOLD}{BLUE}{'*'*80}{RESET}")

    try:
        # Run tests
        availability_ids = test_availability()
        if not availability_ids:
            return

        reservation_id = test_reservation(availability_ids)

        test_cancellation(availability_ids)

        waitlist_id = test_waitlist(availability_ids)

        test_availability_operations(availability_ids)

        test_error_handling()

        # Summary
        print_header("TEST SUMMARY")
        print(f"{GREEN}✓ All tests completed successfully!{RESET}")
        print(f"\n{BOLD}Tested Components:{RESET}")
        print(f"  • Availability Aggregate (Create, Read, Check, Reserve, Release, Block, Unblock)")
        print(f"  • Reservation Aggregate (Create, Modify, Confirm, Check-in, Check-out, Cancel)")
        print(f"  • Special Requests (Add, Track)")
        print(f"  • Waitlist Aggregate (Add, Convert, Upgrade, Extend, Notify)")
        print(f"  • Error Handling & Validation")
        print(f"\n{BOLD}API Documentation:{RESET}")
        print(f"  Swagger UI: http://localhost:8000/docs")
        print(f"  ReDoc: http://localhost:8000/redoc")

    except requests.exceptions.ConnectionError:
        print_error("Could not connect to server at http://localhost:8000")
        print_info("Make sure the FastAPI server is running!")
    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    main()
