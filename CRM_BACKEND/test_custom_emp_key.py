import requests
import json
import os
import Database

BASE_URL = "http://127.0.0.1:8000"

def test_custom_key_assignment():
    print("--- Starting CRM Custom Employee Key Assignment Test ---")
    
    # 0. Clean up any leftover test data first
    print("\n0. Cleaning up any leftover test data...")
    Database.db_execute("DELETE FROM users WHERE email IN ('manual_key@test.com', 'convert_manual@test.com', 'convert_dup@test.com')")
    Database.db_execute("DELETE FROM employee_leads WHERE email IN ('convert_manual@test.com', 'convert_dup@test.com')")
    
    # 1. Login as Admin
    print("\n1. Logging in as Admin...")
    login_payload = {
        "employee_id": "admin",
        "password": "admin123"
    }
    r = requests.post(f"{BASE_URL}/login", json=login_payload)
    if r.status_code != 200:
        print(f"FAILED to log in: {r.status_code} - {r.text}")
        return
    
    login_data = r.json()
    token = login_data.get("token") or login_data.get("access_token")
    print(f"SUCCESS: Logged in. Token: {token[:15]}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test Signup with manual employee_id
    print("\n2. Testing Signup with MANUAL employee_id...")
    manual_eid = "MANUAL-EMP-101"
    signup_payload = {
        "name": "Manual Key Employee",
        "email": "manual_key@test.com",
        "phone": "9999999999",
        "password": "password123",
        "role": "sales",
        "employee_id": manual_eid
    }
    r_signup = requests.post(f"{BASE_URL}/signup", json=signup_payload, headers=headers)
    print(f"Signup response status: {r_signup.status_code}")
    print(f"Signup response content: {r_signup.text}")
    assert r_signup.status_code == 200
    signup_data = r_signup.json()
    assert signup_data.get("employee_id") == manual_eid
    print("SUCCESS: Signup with custom key succeeded.")

    # Try to signup with the same manual ID again (should fail)
    print("\n2b. Testing Signup duplicate manual employee_id validation...")
    signup_payload_dup = {
        "name": "Manual Key Employee Duplicate",
        "email": "manual_key_dup@test.com",
        "phone": "9999999999",
        "password": "password123",
        "role": "sales",
        "employee_id": manual_eid
    }
    r_dup = requests.post(f"{BASE_URL}/signup", json=signup_payload_dup, headers=headers)
    print(f"Duplicate signup status (Expected 400): {r_dup.status_code}")
    assert r_dup.status_code == 400
    print("SUCCESS: Duplicate ID validation works correctly.")

    # 3. Test Lead Conversion with manual employee_id
    print("\n3. Creating an Employee Lead for Conversion...")
    lead_data = {
        "name": "Lead Convert Candidate",
        "email": "convert_manual@test.com",
        "phone": "8888888888",
        "role": "sales"
    }
    r_lead = requests.post(f"{BASE_URL}/employee-leads", data=lead_data, headers=headers)
    assert r_lead.status_code == 200
    
    # Get Lead ID
    r_list = requests.get(f"{BASE_URL}/employee-leads", headers=headers)
    leads = r_list.json().get("leads", [])
    target_lead = next((l for l in leads if l["email"] == "convert_manual@test.com"), None)
    assert target_lead is not None
    lead_id = target_lead["id"]
    print(f"SUCCESS: Created lead with ID: {lead_id}")

    print("\n3b. Converting Lead with MANUAL employee_id...")
    manual_convert_eid = "MANUAL-CONV-202"
    convert_payload = {
        "password": "candidatepass123",
        "salary": 35000,
        "department": "Engineering",
        "designation": "Software Engineer",
        "biometric_id": "111",
        "employee_id": manual_convert_eid
    }
    r_convert = requests.post(
        f"{BASE_URL}/employee-leads/{lead_id}/convert",
        json=convert_payload,
        headers=headers
    )
    print(f"Conversion response status: {r_convert.status_code}")
    print(f"Conversion response content: {r_convert.text}")
    assert r_convert.status_code == 200
    convert_data = r_convert.json()
    assert convert_data.get("employee_id") == manual_convert_eid
    print("SUCCESS: Conversion with custom key succeeded.")

    # Try duplicate ID during conversion
    print("\n3c. Testing Lead Conversion duplicate ID validation...")
    # Create another lead
    lead_data_2 = {
        "name": "Second Candidate",
        "email": "convert_dup@test.com",
        "phone": "7777777777",
        "role": "sales"
    }
    r_lead2 = requests.post(f"{BASE_URL}/employee-leads", data=lead_data_2, headers=headers)
    assert r_lead2.status_code == 200
    
    r_list2 = requests.get(f"{BASE_URL}/employee-leads", headers=headers)
    leads2 = r_list2.json().get("leads", [])
    target_lead2 = next((l for l in leads2 if l["email"] == "convert_dup@test.com"), None)
    lead_id2 = target_lead2["id"]
    
    # Try to convert with the same custom key `MANUAL-CONV-202`
    convert_payload2 = {
        "password": "candidatepass123",
        "salary": 35000,
        "department": "Engineering",
        "designation": "Software Engineer",
        "biometric_id": "112",
        "employee_id": manual_convert_eid
    }
    r_convert_dup = requests.post(
        f"{BASE_URL}/employee-leads/{lead_id2}/convert",
        json=convert_payload2,
        headers=headers
    )
    print(f"Duplicate conversion status (Expected 400): {r_convert_dup.status_code}")
    assert r_convert_dup.status_code == 400
    print("SUCCESS: Duplicate ID validation in lead conversion works correctly.")

    # 4. Clean up test users and leads
    print("\n4. Cleaning up database...")
    # Delete test users
    Database.db_execute("DELETE FROM users WHERE email IN ('manual_key@test.com', 'convert_manual@test.com', 'convert_dup@test.com')")
    Database.db_execute("DELETE FROM employee_leads WHERE id IN (%s, %s)", (lead_id, lead_id2))
    Database.pool.close()
    print("SUCCESS: Cleaned up database.")
    print("\n--- All Tests Passed Successfully! ---")

if __name__ == "__main__":
    test_custom_key_assignment()
