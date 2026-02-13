from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
import os

load_dotenv()

token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
print(f"Token present: {bool(token)}")

try:
    repo = "HuggingFaceH4/zephyr-7b-beta"
    task = "text-generation"
    print(f"Initializing {repo} with task={task}")
    llm = HuggingFaceEndpoint(
        repo_id=repo,
        task=task,
        huggingfacehub_api_token=token
    )
    print("Model initialized.")
    response = llm.invoke("Hello, are you working?")
    print(f"Response: {response}")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
