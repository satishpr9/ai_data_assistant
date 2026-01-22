from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_classic.chains import RetrievalQA
from app.vectorstore import get_hybrid_retriever
import os


def ask_question(question):
    """
    RAG (Retrieval-Augmented Generation) pipeline with HYBRID SEARCH
    
    Process:
    1. Get hybrid retriever (FAISS + BM25)
    2. Initialize language model
    3. Create RetrievalQA chain
    4. Invoke with question
    
    Args:
        question: user's question to answer
    
    Returns:
        string: LLM answer based on retrieved documents
    
    Example:
        >>> answer = ask_question("Tell me about Q3 sales")
        >>> print(answer)
    """
    
    # Step 1: Get hybrid retriever combining semantic + keyword search
    retriever = get_hybrid_retriever(k=3)
    
    if retriever is None:
        return "No documents ingested yet. Please upload PDFs or ingest data first."
    
    # Step 2: Initialize HuggingFace language model
    model = HuggingFaceEndpoint(
        repo_id="HuggingFaceH4/zephyr-7b-beta",
        task="conversational",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        temperature=0.2,  # Lower = more focused answers
        max_new_tokens=512,  # Max response length
        top_p=0.95,  # Nucleus sampling
        repetition_penalty=1.15,  # Avoid repetition
    )
    
    # Step 3: Create chat wrapper
    chat = ChatHuggingFace(llm=model, verbose=True)
    
    # Step 4: Create RetrievalQA chain
    # This chains: retrieve documents -> create context -> generate answer
    qa = RetrievalQA.from_chain_type(
        llm=chat,
        chain_type="stuff",  # Simple chain type (concatenates all docs)
        retriever=retriever,
        return_source_documents=False
    )
    
    # Step 5: Invoke the chain with the question
    result = qa.invoke({"query": question})
    
    print(f"✓ RAG answered question: '{question}'")
    return result["result"]