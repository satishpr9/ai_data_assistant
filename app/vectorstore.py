from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_classic.schema import Document
import os

# Initialize embeddings model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

VECTOR_DIR = "data/faiss_index"

# Global variables to store retrievers
vector_db = None  # FAISS for semantic search
bm25_retriever = None  # BM25 for keyword search


def create_vectorstore(texts):
    """
    Create both FAISS (semantic) and BM25 (keyword) indexes
    Called when uploading new PDF
    """
    global vector_db, bm25_retriever
    
    # Create FAISS semantic search index
    vector_db = FAISS.from_texts(texts, embeddings)
    vector_db.save_local(VECTOR_DIR)
    
    # Create BM25 retriever for keyword-based search
    docs = [Document(page_content=text) for text in texts]
    bm25_retriever = BM25Retriever.from_documents(docs)
    
    print(f"✓ Created vectorstore with {len(texts)} chunks")


def get_vectorstore():
    """
    Get FAISS vectorstore
    Loads from disk if not already in memory
    """
    global vector_db
    
    if vector_db is None and os.path.exists(VECTOR_DIR):
        vector_db = FAISS.load_local(
            VECTOR_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✓ Loaded FAISS vectorstore from disk")
    
    return vector_db


def get_bm25_retriever():
    """
    Get BM25 retriever
    Creates from existing FAISS documents if not initialized
    """
    global bm25_retriever, vector_db
    
    if bm25_retriever is None:
        vector_db = get_vectorstore()
        
        if vector_db is not None:
            # Extract all documents from FAISS and create BM25
            docs = list(vector_db.docstore._dict.values())
            bm25_retriever = BM25Retriever.from_documents(docs)
            print("✓ Initialized BM25 retriever from FAISS documents")
    
    return bm25_retriever


def get_hybrid_retriever(k: int = 4):
    """
    Create hybrid retriever combining FAISS and BM25
    
    Args:
        k: number of results to return
    
    Returns:
        EnsembleRetriever with weighted combination
    """
    semantic_retriever = get_vectorstore()
    keyword_retriever = get_bm25_retriever()
    
    if semantic_retriever is None or keyword_retriever is None:
        return None
    
    # Ensemble retriever: combines both search methods
    # weights: [0.6, 0.4] means 60% semantic, 40% keyword
    ensemble_retriever = EnsembleRetriever(
        retrievers=[
            semantic_retriever.as_retriever(search_kwargs={"k": k}),
            keyword_retriever
        ],
        weights=[0.6, 0.4]
    )
    
    print(f"✓ Created hybrid retriever with k={k}")
    return ensemble_retriever


def add_texts(texts: list[str], metadatas: list[dict]):
    """
    Add new texts to both FAISS and BM25
    Called when ingesting MySQL data
    
    Args:
        texts: list of text chunks to add
        metadatas: metadata for each chunk
    """
    global vector_db, bm25_retriever
    
    # Add to FAISS vectorstore
    if vector_db is None:
        # Create new if doesn't exist
        vector_db = FAISS.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas
        )
        print(f"✓ Created FAISS with {len(texts)} texts")
    else:
        # Add to existing
        vector_db.add_texts(
            texts=texts,
            metadatas=metadatas
        )
        print(f"✓ Added {len(texts)} texts to FAISS")
    
    # Save FAISS to disk
    vector_db.save_local(VECTOR_DIR)
    
    # Recreate BM25 with all documents
    docs = list(vector_db.docstore._dict.values())
    bm25_retriever = BM25Retriever.from_documents(docs)
    print(f"✓ Updated BM25 retriever with {len(docs)} documents")