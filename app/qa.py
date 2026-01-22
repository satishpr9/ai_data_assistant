from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_classic.chains import RetrievalQA
from app.vectorstore import get_hybrid_retriever
import os


def ask_question(question):
    """
    RAG (Retrieval-Augmented Generation) pipeline with HYBRID SEARCH
    
    Returns the answer as a STRING (not object)
    """
    
    print(f"\n🤖 RAG Pipeline - Question: {question}")
    
    # Step 1: Get hybrid retriever (FAISS + BM25)
    retriever = get_hybrid_retriever(k=3)
    
    if retriever is None:
        print("⚠️ No vectorstore available")
        return "No documents ingested yet. Please upload PDFs or ingest data first."
    
    print("✓ Hybrid retriever initialized")
    
    # Step 2: Initialize HuggingFace language model
    model = HuggingFaceEndpoint(
        repo_id="HuggingFaceH4/zephyr-7b-beta",
        task="conversational",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        temperature=0.2,
        max_new_tokens=512,
        top_p=0.95,
        repetition_penalty=1.15,
    )
    
    print("✓ LLM initialized")
    
    # Step 3: Create chat wrapper
    chat = ChatHuggingFace(llm=model, verbose=True)
    
    # Step 4: Create RetrievalQA chain
    qa = RetrievalQA.from_chain_type(
        llm=chat,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False
    )
    
    print("✓ QA chain created")
    
    # Step 5: Invoke the chain with the question
    print("📤 Invoking QA chain...")
    result = qa.invoke({"query": question})
    
    # IMPORTANT: Extract the text from result
    # result is a dict like: {"query": "...", "result": "The answer..."}
    # answer_text = result.get("result") if isinstance(result, dict) else str(result)
    answer_text = (result.get("answer") or result.get("result")) if isinstance(result, dict) else str(result)
    print(f"✓ Got answer: {answer_text[:100]}...")
    
    return answer_text