import Database
from auth import hash_password

def check_users():
    users = Database.db_query("SELECT id, name, email, phone, employee_id, role_id, is_active FROM users")
    roles = Database.db_query("SELECT id, role_name FROM roles")
    
    print("--- ROLES ---")
    for r in roles:
        print(f"Role ID: {r['id']}, Name: {r['role_name']}")
        
    print("\n--- USERS ---")
    for u in users:
        print(f"ID: {u['id']}, Name: {u['name']}, Email: {u['email']}, EmpID: {u['employee_id']}, RoleID: {u['role_id']}, Active: {u['is_active']}")

if __name__ == "__main__":
    check_users()
