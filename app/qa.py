from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from .retriever import retrieve_documents
import os
llm=HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")

)
chat=ChatHuggingFace(llm=llm,verbose=True)

def answer_question(query:str):
    docs=retrieve_documents(query)

    if not docs:
        return{
            "answer":"No documents ingested yet",
            "sources":[]
        }
    context="\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Use the context below to answer the question.
If the answer is not in the context, say you don't know.

Context:
{context}

Question:
{query}
"""

    response=chat.invoke(prompt)
    sources=[]
    for doc in docs:
        sources.append(doc.metadata)
    return {
        "answer":response,
        "sources":sources
    }