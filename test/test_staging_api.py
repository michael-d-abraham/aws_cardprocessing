import json
import os
import sys
import requests

BASE_URL = os.environ["STAGING_API_URL"]

# Adjust these to match your actual Lambda/API expectations
GOOD_PAYLOAD = {
    "cardNumber": "4111111111111111",
    "expMonth": "12",
    "expYear": "2030",
    "cvv": "123",
    "amount": 100
}

BAD_PAYLOADS = [
    ("missing body", None),
    ("empty json", {}),
    ("missing cardNumber", {
        "expMonth": "12",
        "expYear": "2030",
        "cvv": "123",
        "amount": 100
    }),
    ("bad amount type", {
        "cardNumber": "4111111111111111",
        "expMonth": "12",
        "expYear": "2030",
        "cvv": "123",
        "amount": "abc"
    }),
]

def log_failure(name, expected, actual_status, actual_body):
    print(f"\n[FAIL] {name}")
    print(f"Expected: {expected}")
    print(f"Actual status: {actual_status}")
    print("Actual body:")
    print(actual_body)

def run_request(name, payload, expected_status, headers=None):
    headers = headers or {"Content-Type": "application/json"}

    try:
        if payload is None:
            response = requests.post(BASE_URL, headers=headers)
        else:
            response = requests.post(BASE_URL, headers=headers, json=payload)
    except Exception as e:
        print(f"\n[FAIL] {name}")
        print(f"Request error: {e}")
        return False

    ok = response.status_code == expected_status
    if not ok:
        try:
            body = response.json()
        except Exception:
            body = response.text
        log_failure(name, expected_status, response.status_code, body)

    return ok

def main():
    failures = 0

    # 1. Happy path
    if not run_request("valid request", GOOD_PAYLOAD, 200):
        failures += 1

    # 2. Bad payloads
    for name, payload in BAD_PAYLOADS:
        if not run_request(name, payload, 400):
            failures += 1

    # 3. Bad auth example
    # Only keep this if your API actually uses auth
    # bad_auth_headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": "Bearer definitely-invalid"
    # }
    # if not run_request("bad auth", GOOD_PAYLOAD, 401, headers=bad_auth_headers):
    #     failures += 1

    if failures:
        print(f"\nTest run complete: {failures} failure(s)")
        sys.exit(1)

    print("\nAll staging API tests passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()