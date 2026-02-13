import requests
import sys

API_URL = "http://localhost:8000"

def test_rbac():
    # 1. Register a normal user
    username = "test_user_rbac"
    password = "password123"
    print(f"Registering standard user: {username}")
    res = requests.post(f"{API_URL}/auth/register", json={"username": username, "email": f"{username}@test.com", "password": password})
    
    if res.status_code == 200 or res.status_code == 201:
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")
        
        # 2. Try to access admin endpoint (should fail)
        print("Attempting to access admin endpoint /ingest/mysql...")
        res = requests.post(f"{API_URL}/ingest/mysql", headers=headers)
        if res.status_code == 403:
            print("PASS: Access denied (403) as expected.")
        else:
            print(f"FAIL: Unexpected status code {res.status_code}")
            
    else:
        # Try login if already exists
        res = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
        if res.status_code == 200:
            token = res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("Login successful (user existed).")
            
            # 2. Try to access admin endpoint (should fail)
            print("Attempting to access admin endpoint /ingest/mysql...")
            res = requests.post(f"{API_URL}/ingest/mysql", headers=headers)
            if res.status_code == 403:
                print("PASS: Access denied (403) as expected.")
            else:
                print(f"FAIL: Unexpected status code {res.status_code}")
        else:
            print(f"Failed to register/login: {res.text}")
            return

    # 3. Promote user to admin (requires external script execution, mocking here by assuming we run promote_user.py)
    # Since we can't run the script from within this python script easily without subprocess, 
    # we will just print instruction or use a separate admin user if we had one.
    
    print("\nTo test admin access, run: python promote_user.py test_user_rbac")
    print("Then re-run this script with argument 'admin'")

def test_admin_access():
    username = "test_user_rbac"
    password = "password123"
    
    print(f"\nLogging in as promoted user: {username}")
    res = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
    
    if res.status_code == 200:
        token = res.json()["access_token"]
        user = res.json()["user"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"Role in response: {user.get('role')}")
        
        if user.get('role') == 'admin':
            print("PASS: User role is 'admin'.")
        else:
            print("FAIL: User role is NOT 'admin'.")
            
        # Try admin endpoint
        print("Attempting to access admin endpoint /ingest/mysql...")
        res = requests.post(f"{API_URL}/ingest/mysql", headers=headers)
        if res.status_code == 200:
             print("PASS: Access granted (200).")
        else:
             print(f"FAIL: Access denied with status {res.status_code} (Response: {res.text})")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "admin":
        test_admin_access()
    else:
        test_rbac()
