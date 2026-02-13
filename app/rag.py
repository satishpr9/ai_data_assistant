from langchain_openai import ChatOpenAI
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from app.vectorstore import get_hybrid_retriever
import os

# RAG Prompt Template
prompt_template = """
You are a helpful AI assistant. Use the following pieces of context to answer the question at the end.
If the answer is not in the context, say "I don't have enough information to answer that based on the provided documents."

Context:
{context}

Question: {question}

Answer:
"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

def ask_question(query: str):
    """
    Standard RAG Query (Non-streaming)
    """
    retriever = get_hybrid_retriever(k=3)
    
    if not retriever:
        return "Please upload a document first to start chatting."
    
    # Initialize LLM with Hugging Face Router
    # Using Meta-Llama-3-8B-Instruct via OpenAI-compatible endpoint
    llm = ChatOpenAI(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        openai_api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        openai_api_base="https://router.huggingface.co/v1",
        temperature=0.2,
        max_tokens=512,
    )
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=False
    )
    
    try:
        response = qa.invoke({"query": query})
        return response['result']
    except Exception as e:
        print(f"Error during RAG: {e}")
        return "I encountered an error while processing your request. Please try again."