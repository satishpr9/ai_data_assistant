from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import os

load_dotenv()

token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
print(f"Token present: {bool(token)}")

client = InferenceClient(model="gpt2", token=token)

try:
    print("Sending request...")
    output = client.text_generation("Hello, are you working?", max_new_tokens=20)
    print(f"Response: {output}")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
