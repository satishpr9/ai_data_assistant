from langchain_community.llms import HuggingFaceHub
from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from langchain_classic.chains import RetrievalQA
from app.vectorstore import get_vectorstore
import os 

#RAG PIPELINE
def ask_question(question):
    vector_db=get_vectorstore()

    if vector_db is None:
        return " No documents ingested yet"
    
    model=HuggingFaceEndpoint(
        repo_id="HuggingFaceH4/zephyr-7b-beta",
        task="converstional",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        temperature=0.2,
        max_new_tokens=512,
        top_p= 0.95,
        repetition_penalty=1.15,
        model_kwargs={
            }
    )

    chat = ChatHuggingFace(llm=model, verbose=True)

    qa=RetrievalQA.from_chain_type(
        llm=chat,
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs={"k":3}),
        return_source_documents=False)
    result=qa.invoke({"query":question})
    return result["result"]

