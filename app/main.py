from fastapi import FastAPI,UploadFile,File,HTTPException
import shutil
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.ingest import ingest_pdf
from app.rag import ask_question
import traceback
from app.qa import *
from app.sql_ingest import ingest_business_data
from app.intent import is_chart_query,is_aggregation_query
from app.router import handle_chart_query
from app.analytics import *
app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query:str


@app.post("/upload")
async def upload_pdf(file:UploadFile=File(...)):
    file_path=f"data/uploads/{file.filename}"

    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    chunks=ingest_pdf(file_path)

    return{
        "message":"PDF submitted successfully",
        "chunks_created":chunks
    }


# @app.post("/chat")
# def chat(question:str):
#     answer=ask_question(question)
#     return {"answer":answer}

@app.post("/chat")
async def chat(question: str):
    try:
        answer = ask_question(question)
        return  {"answer": answer}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/ingest/mysql")
def ingest_mysql():
    rows=ingest_business_data()
    return{
        "status":"success",
        "rows_ingested":rows
    }

@app.post("/ask")
async def ask(request:QueryRequest):
    query=request.query
    if is_chart_query(query):
        return {
            "mode": "chart",
            "chart": handle_chart_query(query)
        }

    if is_aggregation_query(query):
        return {
            "mode": "aggregation",
            **top_customer()
        }

    result = ask_question(query)

    if isinstance(result, dict):
        answer = result.get("answer") or result.get("result")
        sources = result.get("sources", [])
    else:
        answer = str(result)
        sources = []

    return {
    "mode": "rag",
    "answer": answer,
    "sources": sources
}
    # return {
    #     "mode": "rag",
    #     **ask_question(query)
    #     }


@app.get("/health")
def health():
    return {"status": "ok"}