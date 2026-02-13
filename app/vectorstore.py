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
    
    # VALIDATION: Filter out None or empty strings
    valid_texts = [t for t in texts if t and isinstance(t, str) and t.strip()]
    
    if not valid_texts:
        print("⚠ No valid texts to index. Skipping vectorstore creation.")
        return

    # Create FAISS semantic search index
    vector_db = FAISS.from_texts(valid_texts, embeddings)
    vector_db.save_local(VECTOR_DIR)
    
    # Create BM25 retriever for keyword-based search
    docs = [Document(page_content=text) for text in valid_texts]
    bm25_retriever = BM25Retriever.from_documents(docs)
    
    print(f"✓ Created vectorstore with {len(valid_texts)} chunks")


def get_vectorstore():
    """
    Get FAISS vectorstore
    Loads from disk if not already in memory
    """
    global vector_db
    
    if vector_db is None and os.path.exists(VECTOR_DIR):
        try:
            vector_db = FAISS.load_local(
                VECTOR_DIR,
                embeddings,
                allow_dangerous_deserialization=True
            )
            print("✓ Loaded FAISS vectorstore from disk")
        except Exception as e:
            print(f"⚠ Failed to load FAISS index: {e}")
            return None
    
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
            try:
                all_docs = list(vector_db.docstore._dict.values())
                # VALIDATION: Filter out None or empty page_content
                docs = [d for d in all_docs if isinstance(d, Document) and d.page_content and isinstance(d.page_content, str) and d.page_content.strip()]
                
                if not docs:
                    print("⚠ No valid documents found for BM25")
                    return None
                    
                bm25_retriever = BM25Retriever.from_documents(docs)
                print(f"✓ Initialized BM25 retriever from {len(docs)} FAISS documents")
            except Exception as e:
                print(f"⚠ Error initializing BM25: {e}")
                return None
    
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
    try:
        ensemble_retriever = EnsembleRetriever(
            retrievers=[
                semantic_retriever.as_retriever(search_kwargs={"k": k}),
                keyword_retriever
            ],
            weights=[0.6, 0.4]
        )
        
        print(f"✓ Created hybrid retriever with k={k}")
        return ensemble_retriever
    except Exception as e:
        print(f"⚠ Error creating hybrid retriever: {e}")
        return None


def add_texts(texts: list[str], metadatas: list[dict]):
    """
    Add new texts to both FAISS and BM25
    Called when ingesting MySQL data
    
    Args:
        texts: list of text chunks to add
        metadatas: metadata for each chunk
    """
    global vector_db, bm25_retriever
    
    # VALIDATION: Filter out None or empty strings
    # We must also filter metadatas to match the filtered texts
    valid_data = []
    for i, t in enumerate(texts):
        if t and isinstance(t, str) and t.strip():
             valid_data.append((t, metadatas[i] if i < len(metadatas) else {}))
    
    if not valid_data:
        print("⚠ No valid texts to add. Skipping.")
        return

    valid_texts, valid_metadatas = zip(*valid_data)
    valid_texts = list(valid_texts)
    valid_metadatas = list(valid_metadatas)
    
    # Add to FAISS vectorstore
    if vector_db is None:
        # Create new if doesn't exist
        vector_db = FAISS.from_texts(
            texts=valid_texts,
            embedding=embeddings,
            metadatas=valid_metadatas
        )
        print(f"✓ Created FAISS with {len(valid_texts)} texts")
    else:
        # Add to existing
        vector_db.add_texts(
            texts=valid_texts,
            metadatas=valid_metadatas
        )
        print(f"✓ Added {len(valid_texts)} texts to FAISS")
    
    # Save FAISS to disk
    vector_db.save_local(VECTOR_DIR)
    
    # Recreate BM25 with all documents
    try:
        docs = list(vector_db.docstore._dict.values())
        # Filter again just in case the store has old bad data
        valid_docs = [d for d in docs if isinstance(d, Document) and d.page_content and isinstance(d.page_content, str)]
        if valid_docs:
            bm25_retriever = BM25Retriever.from_documents(valid_docs)
            print(f"✓ Updated BM25 retriever with {len(valid_docs)} documents")
    except Exception as e:
         print(f"⚠ Error updating BM25: {e}")