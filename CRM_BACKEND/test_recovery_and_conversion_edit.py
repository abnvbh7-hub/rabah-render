import requests
import json
import os
import Database

BASE_URL = "http://127.0.0.1:8000"

def test_recovery_and_conversion_edit():
    print("--- Starting CRM Password Recovery & Conversion Edit Integration Test ---")
    
    # 1. Login as Admin
    print("\n1. Logging in as Admin...")
    login_payload = {
        "employee_id": "abnvbh7@gmail.com",
        "password": "admin123"
    }
    r = requests.post(f"{BASE_URL}/login", json=login_payload)
    if r.status_code != 200:
        print(f"FAILED to log in: {r.status_code} - {r.text}")
        return
    
    login_data = r.json()
    token = login_data.get("token") or login_data.get("access_token")
    print(f"SUCCESS: Logged in. Token starts with: {token[:15] if token else None}")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create an Employee Lead
    print("\n2. Creating an Employee Lead...")
    lead_data = {
        "name": "Edit Test Candidate",
        "email": "edit_test_int@test.com",
        "phone": "1234567890",
        "role": "sales"
    }
    r_lead = requests.post(f"{BASE_URL}/employee-leads", data=lead_data, headers=headers)
    if r_lead.status_code != 200:
        print(f"FAILED to create lead: {r_lead.status_code} - {r_lead.text}")
        return
    print(f"SUCCESS: Lead created.")

    # Get Lead ID
    r_list = requests.get(f"{BASE_URL}/employee-leads", headers=headers)
    leads = r_list.json().get("leads", [])
    target_lead = next((l for l in leads if l["email"] == "edit_test_int@test.com"), None)
    if not target_lead:
        print("FAILED: Lead not found")
        return
    lead_id = target_lead["id"]

    # 3. Convert lead to employee WITH EDITED DETAILS
    print("\n3. Converting lead to employee with modified candidate details...")
    convert_payload = {
        "password": "initial_password_123",
        "salary": 45000,
        "department": "Human Resources",
        "designation": "HR Generalist",
        "biometric_id": "808",
        # Modified details:
        "name": "Fully Edited Candidate Name",
        "email": "edited_email_int@test.com",
        "phone": "9999999999",
        "role": "hr" # should generate a HR prefix instead of SAL
    }
    r_convert = requests.post(
        f"{BASE_URL}/employee-leads/{lead_id}/convert",
        json=convert_payload,
        headers=headers
    )
    if r_convert.status_code != 200:
        print(f"FAILED to convert: {r_convert.status_code} - {r_convert.text}")
        return
    
    convert_res = r_convert.json()
    new_employee_id = convert_res.get("employee_id")
    print(f"SUCCESS: Converted. New Employee ID: {new_employee_id} (Expected prefix: HR)")
    assert new_employee_id.startswith("HR"), f"Expected ID prefix HR, got {new_employee_id}"

    # Verify that the lead table itself is updated
    db_lead = Database.db_query("SELECT * FROM employee_leads WHERE id = %s", (lead_id,), fetch_one=True)
    print(f"Verified lead updated in db: Name={db_lead['name']}, Email={db_lead['email']}, Role={db_lead['role']}")
    assert db_lead["name"] == "Fully Edited Candidate Name"
    assert db_lead["email"] == "edited_email_int@test.com"

    # Verify that the user table has the correct data
    db_user = Database.db_query("SELECT * FROM users WHERE email = %s", ("edited_email_int@test.com",), fetch_one=True)
    print(f"Verified user created in db: Name={db_user['name']}, Email={db_user['email']}, Phone={db_user['phone']}")
    assert db_user["name"] == "Fully Edited Candidate Name"
    assert db_user["phone"] == "9999999999"

    # 4. Verify login with initial password
    print("\n4. Logging in with converted employee credentials...")
    login_user_payload = {
        "employee_id": new_employee_id,
        "password": "initial_password_123"
    }
    r_user_login = requests.post(f"{BASE_URL}/login", json=login_user_payload)
    if r_user_login.status_code != 200:
        print(f"FAILED: User cannot login: {r_user_login.text}")
        return
    print("SUCCESS: Converted user logged in successfully.")

    # 5. Forgot Password Request
    print("\n5. Testing Forgot Password OTP request...")
    r_forgot = requests.post(f"{BASE_URL}/forgot-password", json={"employee_id": new_employee_id})
    if r_forgot.status_code != 200:
        print(f"FAILED forgot request: {r_forgot.text}")
        return
    forgot_res = r_forgot.json()
    print(f"SUCCESS: OTP request completed. Response: {forgot_res}")

    # 6. Retrieve OTP from Database and reset password
    print("\n6. Fetching OTP from database and resetting password...")
    db_otp = Database.db_query("SELECT otp FROM password_otps WHERE email = %s ORDER BY id DESC LIMIT 1", ("edited_email_int@test.com",), fetch_one=True)
    if not db_otp:
        print("FAILED: OTP record not found in database")
        return
    otp_code = db_otp["otp"]
    print(f"SUCCESS: Found OTP code in DB: {otp_code}")

    # Reset Password Call
    reset_payload = {
        "employee_id": new_employee_id,
        "otp": otp_code,
        "new_password": "new_super_secure_password_999"
    }
    r_reset = requests.post(f"{BASE_URL}/reset-password", json=reset_payload)
    if r_reset.status_code != 200:
        print(f"FAILED reset password: {r_reset.text}")
        return
    print("SUCCESS: Password reset successfully.")

    # Verify old password fails
    print("\n7. Verifying login with OLD password fails...")
    r_old_login = requests.post(f"{BASE_URL}/login", json={
        "employee_id": new_employee_id,
        "password": "initial_password_123"
    })
    print(f"Old login status (Expected 400): {r_old_login.status_code}")
    assert r_old_login.status_code == 400

    # Verify login with NEW password succeeds
    print("Verifying login with NEW password succeeds...")
    r_new_login = requests.post(f"{BASE_URL}/login", json={
        "employee_id": new_employee_id,
        "password": "new_super_secure_password_999"
    })
    print(f"New login status (Expected 200): {r_new_login.status_code}")
    assert r_new_login.status_code == 200
    print("SUCCESS: Logged in successfully with new password.")

    # 8. Cleanup Database
    print("\n8. Cleaning up database records...")
    Database.db_execute("DELETE FROM attendance WHERE user_id = (SELECT id FROM users WHERE email = %s)", ("edited_email_int@test.com",))
    Database.db_execute("DELETE FROM users WHERE email = %s", ("edited_email_int@test.com",))
    Database.db_execute("DELETE FROM password_otps WHERE email = %s", ("edited_email_int@test.com",))
    Database.db_execute("DELETE FROM employee_leads WHERE id = %s", (lead_id,))
    print("SUCCESS: Database cleaned up and test completed successfully.")
    print("\n--- All Recovery and Edit-on-Convert Tests Passed Successfully! ---")

if __name__ == "__main__":
    test_recovery_and_conversion_edit()
