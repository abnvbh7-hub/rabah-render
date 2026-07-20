import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"

def test_onboarding_pipeline():
    print("--- Starting CRM Employee Onboarding Flow Integration Test ---")
    
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
    token = login_data.get("token")
    if not token:
        # Check if response has access_token or token
        token = login_data.get("access_token")
    
    print(f"SUCCESS: Logged in. Token starts with: {token[:15] if token else None}")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Public signups should be protected
    print("\n2. Testing public signup restriction...")
    signup_payload = {
        "name": "Intruder User",
        "email": "intruder@evil.com",
        "phone": "9999999999",
        "password": "somepassword",
        "role": "sales"
    }
    # Call without auth headers
    r_pub = requests.post(f"{BASE_URL}/signup", json=signup_payload)
    print(f"Public call status code (Expected 401/403): {r_pub.status_code}")
    assert r_pub.status_code in (401, 403), "Signup endpoint is publicly accessible!"
    print("SUCCESS: Public signup is restricted.")
    
    # 3. Create an Employee Lead with PDF resume upload
    print("\n3. Creating an Employee Lead with resume upload...")
    dummy_pdf_path = "../dummy.pdf"
    if not os.path.exists(dummy_pdf_path):
        # try local path
        dummy_pdf_path = "dummy.pdf"
        if not os.path.exists(dummy_pdf_path):
            with open(dummy_pdf_path, "wb") as f:
                f.write(b"%PDF-1.4 dummy contents")
    
    lead_data = {
        "name": "Integration Test Candidate",
        "email": "candidate_test_int@test.com",
        "phone": "9876543210",
        "role": "sales"
    }
    
    with open(dummy_pdf_path, "rb") as f:
        files = {"resume": (os.path.basename(dummy_pdf_path), f, "application/pdf")}
        r_lead = requests.post(
            f"{BASE_URL}/employee-leads",
            data=lead_data,
            files=files,
            headers=headers
        )
    
    if r_lead.status_code != 200:
        print(f"FAILED to create lead: {r_lead.status_code} - {r_lead.text}")
        return
        
    print(f"SUCCESS: Lead created: {r_lead.json()}")
    
    # 4. List Employee Leads to verify existence and get ID
    print("\n4. Fetching employee leads list...")
    r_list = requests.get(f"{BASE_URL}/employee-leads", headers=headers)
    if r_list.status_code != 200:
        print(f"FAILED to list leads: {r_list.status_code} - {r_list.text}")
        return
        
    leads = r_list.json().get("leads", [])
    target_lead = None
    for l in leads:
        if l["email"] == "candidate_test_int@test.com":
            target_lead = l
            break
            
    if not target_lead:
        print("FAILED: Target lead not found in list")
        return
        
    lead_id = target_lead["id"]
    resume_path = target_lead["resume_path"]
    print(f"SUCCESS: Found target lead with ID: {lead_id}, Resume Path: {resume_path}")
    
    # Verify that the resume static serving is hosting the file
    if resume_path:
        r_resume = requests.get(f"{BASE_URL}{resume_path}")
        print(f"Resume static file request status (Expected 200): {r_resume.status_code}")
        assert r_resume.status_code == 200, "Resume file is not served publicly/statically"
        print("SUCCESS: Static file hosting is serving the resume correctly.")

    # 5. Convert lead to employee
    print("\n5. Converting lead to active employee...")
    convert_payload = {
        "password": "candidatepass123",
        "salary": 32000,
        "department": "Sales Division",
        "designation": "Sales Executive Associate",
        "biometric_id": "909"
    }
    
    r_convert = requests.post(
        f"{BASE_URL}/employee-leads/{lead_id}/convert",
        json=convert_payload,
        headers=headers
    )
    
    if r_convert.status_code != 200:
        print(f"FAILED to convert lead: {r_convert.status_code} - {r_convert.text}")
        return
        
    convert_res = r_convert.json()
    new_employee_id = convert_res.get("employee_id")
    print(f"SUCCESS: Converted lead. New Employee ID: {new_employee_id}")
    
    # 6. Verify Login credentials of converted employee
    print("\n6. Logging in with converted employee credentials...")
    new_login_payload = {
        "employee_id": new_employee_id,
        "password": "candidatepass123"
    }
    r_new_login = requests.post(f"{BASE_URL}/login", json=new_login_payload)
    if r_new_login.status_code != 200:
        print(f"FAILED: Converted employee cannot log in: {r_new_login.status_code} - {r_new_login.text}")
        return
    print(f"SUCCESS: Converted employee logged in successfully!")
    
    # 7. Clean up database to leave workspace pristine
    print("\n7. Cleaning up test data...")
    # Delete from attendance first
    import Database
    Database.db_execute("DELETE FROM attendance WHERE user_id = (SELECT id FROM users WHERE email = %s)", ("candidate_test_int@test.com",))
    # Delete from users
    Database.db_execute("DELETE FROM users WHERE email = %s", ("candidate_test_int@test.com",))
    # Delete lead
    r_del = requests.delete(f"{BASE_URL}/employee-leads/{lead_id}", headers=headers)
    print(f"Lead delete result status code: {r_del.status_code}")
    print("SUCCESS: Database cleaned up.")
    
    print("\n--- All Integration Tests Passed Successfully! ---")

if __name__ == "__main__":
    test_onboarding_pipeline()
