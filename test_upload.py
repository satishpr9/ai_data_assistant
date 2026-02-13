
import requests

API_URL = "http://localhost:8000"

def test_upload_txt():
    # Create a dummy txt file
    with open("test.txt", "w") as f:
        f.write("This is a test text file content for RAG ingestion.")
    
    # Login to get token (assuming test_user exists or we can register)
    # For simplicity, let's assume we need to register/login
    # But wait, I can just use the token from headers if I had it.
    # I'll try to login with default credentials if possible or just use a new user
    
    # Register/Login flow
    username = "test_upload_user"
    password = "password123"
    
    # Register
    requests.post(f"{API_URL}/auth/register", json={"username": username, "email": "test@test.com", "password": password})
    
    # Login
    resp = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
    if resp.status_code != 200:
        print("Login failed")
        return
        
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload
    with open("test.txt", "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        resp = requests.post(f"{API_URL}/upload", headers=headers, files=files)
        
    print(f"Upload TXT Status: {resp.status_code}")
    print(f"Upload TXT Response: {resp.json()}")

if __name__ == "__main__":
    test_upload_txt()
