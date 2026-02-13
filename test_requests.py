import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
headers = {"Authorization": f"Bearer {token}"}
# Test 1: hf-inference path
API_URL_1 = "https://router.huggingface.co/hf-inference/models/gpt2"
payload_1 = {"inputs": "Hello"}

# Test 2: OpenAI compatible path
API_URL_2 = "https://router.huggingface.co/v1/chat/completions"
payload_2 = {
    "model": "meta-llama/Meta-Llama-3-8B-Instruct",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": True
}

def test_url(url, json_data):
    try:
        print(f"Testing {url}...")
        response = requests.post(url, headers=headers, json=json_data)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

test_url(API_URL_1, payload_1)
print("-" * 20)
test_url(API_URL_2, payload_2)
