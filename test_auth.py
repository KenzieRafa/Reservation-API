#!/usr/bin/env python3
"""
Test script untuk Authentication
"""

import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000"

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def test_auth():
    print("\n=== TESTING AUTHENTICATION ===\n")

    # 1. Test Login (Success)
    print("1. Testing Login (Success)...")
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/token", data=payload)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print_success("Login successful")
        print(f"   Token: {access_token[:20]}...")
    else:
        print_error(f"Login failed: {response.text}")
        return

    # 2. Test Login (Failure)
    print("\n2. Testing Login (Failure)...")
    payload = {
        "username": "admin",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/token", data=payload)
    if response.status_code == 401:
        print_success("Login failed as expected")
    else:
        print_error(f"Login should have failed but got {response.status_code}")

    # 3. Test Protected Endpoint (Without Token)
    print("\n3. Testing Protected Endpoint (Without Token)...")
    reservation_payload = {
        "guest_id": str(uuid4()),
        "room_type_id": "DELUXE_001",
        "check_in": "2025-12-20",
        "check_out": "2025-12-22",
        "adults": 2,
        "children": 0
    }
    response = requests.post(f"{BASE_URL}/api/reservations", json=reservation_payload)
    if response.status_code == 401:
        print_success("Access denied as expected")
    else:
        print_error(f"Should be 401 but got {response.status_code}")

    # 4. Test Protected Endpoint (With Token)
    print("\n4. Testing Protected Endpoint (With Token)...")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(f"{BASE_URL}/api/reservations", json=reservation_payload, headers=headers)
    if response.status_code == 201:
        print_success("Access granted and reservation created")
    else:
        print_error(f"Failed to create reservation: {response.text}")

    # 5. Test Protected GET Endpoint (Without Token)
    print("\n5. Testing Protected GET Endpoint (Without Token)...")
    response = requests.get(f"{BASE_URL}/api/reservations")
    if response.status_code == 401:
        print_success("Access denied as expected for GET request")
    else:
        print_error(f"Should be 401 but got {response.status_code}")

if __name__ == "__main__":
    try:
        test_auth()
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to server. Make sure it is running!")
