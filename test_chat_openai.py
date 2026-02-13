from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

import logging
import httpx

# Enable logging
logging.basicConfig(level=logging.INFO)
def print_debug(r):
    print(f"DEBUG: Request Headers: {r.headers}")
    print(f"DEBUG: Request Body: {r.content}")

http_client = httpx.Client(event_hooks={'request': [print_debug]})

token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Force Authorization header manually
llm = ChatOpenAI(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    api_key="dummy", # Use dummy key as we set header manually
    base_url="https://router.huggingface.co/v1",
    default_headers={"Authorization": f"Bearer {token}"},
    http_client=http_client
)

try:
    print("Invoking ChatOpenAI...")
    response = llm.invoke("Hello")
    print(response.content)
except Exception as e:
    print(f"Error: {e}")
