from app.vectorstore import get_vectorstore, get_bm25_retriever
from langchain_classic.schema import Document

print("Loading vectorstore...")
try:
    db = get_vectorstore()
    if db:
        print(f"FAISS index loaded. Document count: {len(db.docstore._dict)}")
        
        print("\nChecking for invalid documents in FAISS...")
        invalid_count = 0
        for doc_id, doc in db.docstore._dict.items():
            if not isinstance(doc, Document):
                print(f"WARNING: Item {doc_id} is not a Document: {type(doc)}")
                invalid_count += 1
            elif not doc.page_content:
                print(f"WARNING: Document {doc_id} has empty content: {doc.page_content}")
                invalid_count += 1
            elif not isinstance(doc.page_content, str):
                print(f"WARNING: Document {doc_id} content is not string: {type(doc.page_content)}")
                invalid_count += 1
        
        if invalid_count == 0:
            print("✓ All FAISS documents appear valid.")
        else:
            print(f"Found {invalid_count} invalid documents.")

    else:
        print("No FAISS index found.")

    print("\nChecking BM25 retriever...")
    retriever = get_bm25_retriever()
    if retriever:
        print(f"BM25 retriever initialized successfully with {len(retriever.docs)} docs.")
    else:
        print("BM25 retriever failed to initialize (expected if no valid docs).")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
