from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores  import FAISS
import os

embeddings=HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
VECTOR_DIR = "data/faiss_index"
vector_db=None

#embeddings into FAISS(Vector DataBase) 
#and save faiss database as local
def create_vectorstore(texts):
    global vector_db
    vector_db=FAISS.from_texts(texts,embeddings)
    vector_db.save_local(VECTOR_DIR)

def get_vectorstore():
    global vector_db

    if vector_db is None and os.path.exists(VECTOR_DIR):
        vector_db=FAISS.load_local(
            VECTOR_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )
    return vector_db

   
def add_texts(texts: list[str], metadatas: list[dict]):
    global vector_db

    if vector_db is None:
        vector_db = FAISS.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas
        )
    else:
        vector_db.add_texts(
            texts=texts,
            metadatas=metadatas
        )

    vector_db.save_local(VECTOR_DIR)

