from fastapi import FastAPI,UploadFile,File,HTTPException
import shutil
from app.ingest import ingest_pdf
from app.rag import ask_question
import traceback
from app.qa import answer_question
from app.sql_ingest import ingest_business_data
app=FastAPI()

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
def ask_question(query:str):
    return answer_question(query)