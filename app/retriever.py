from app.vectorstore import get_vectorstore

def retrieve_documents(query:str,k:int=4):
    vectorstore=get_vectorstore()

    if not vectorstore:
        return []
    docs =vectorstore.similarity_search(query,k=k)
    return docs
