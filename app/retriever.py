from app.vectorstore import get_hybrid_retriever


def retrieve_documents(query: str, k: int = 3):
    """
    Retrieve documents using HYBRID SEARCH
    
    Combines:
    1. Semantic Search (FAISS) - understands meaning & intent
    2. Keyword Search (BM25) - exact term matching
    
    Args:
        query: user's search query
        k: number of documents to return
    
    Returns:
        list of Document objects with content and metadata
    
    Example:
        >>> docs = retrieve_documents("sales in January")
        >>> for doc in docs:
        ...     print(doc.page_content)
    """
    
    # Get the hybrid retriever (FAISS + BM25)
    retriever = get_hybrid_retriever(k=k)
    
    if not retriever:
        print("⚠ No documents available for retrieval")
        return []
    
    try:
        # Use hybrid retriever to get relevant documents
        # This returns top k documents from combined ranking
        docs = retriever.invoke(query)
        
        print(f"✓ Retrieved {len(docs)} documents for query: '{query}'")
        return docs
        
    except Exception as e:
        print(f"✗ Error in hybrid retrieval: {e}")
        return []