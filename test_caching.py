import requests
import time
import sys

API_URL = "http://localhost:8000"

def test_caching():
    # Login to get token
    username = "test_user_rbac" # Reusing the user we created earlier
    password = "password123"
    
    print(f"Logging in as {username}...")
    res = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
        
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    query = {"query": "What is the capital of France?"} # Simple query that should be cached
    
    print("\n--- Request 1 (Uncached) ---")
    start_time = time.time()
    # We use the streaming endpoint but collect the result
    with requests.post(f"{API_URL}/ask/stream", json=query, headers=headers, stream=True) as r:
        for line in r.iter_lines():
            pass # Consume output
    duration1 = time.time() - start_time
    print(f"Time taken: {duration1:.4f} seconds")
    
    print("\n--- Request 2 (Cached) ---")
    start_time = time.time()
    with requests.post(f"{API_URL}/ask/stream", json=query, headers=headers, stream=True) as r:
        for line in r.iter_lines():
            pass # Consume output
    duration2 = time.time() - start_time
    print(f"Time taken: {duration2:.4f} seconds")
    
    if duration2 < duration1 * 0.5: # Expecting at least 50% speedup (usually much more)
        print("\nPASS: Significant speedup detected (Caching works!)")
    else:
        print("\nWARN: Speedup not significant. Caching might not be working or network latency dominates.")

if __name__ == "__main__":
    test_caching()
