from dotenv import load_dotenv
from app.rag import ask_question
import os

load_dotenv(override=True)

print("Testing RAG with Hugging Face Router...")
try:
    response = ask_question("Hello, are you working?")
    print(f"Response: {response}")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
