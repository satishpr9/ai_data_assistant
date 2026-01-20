from fastapi import FastAPI,UploadFile,File,HTTPException
import shutil
from app.ingest import ingest_pdf
from app.rag import ask_question
import traceback
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