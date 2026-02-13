import os
import json
import pandas as pd
from pypdf import PdfReader
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .vectorstore import create_vectorstore

def ingest_file(path: str) -> int:
    """
    Ingest a file of supported format into the vectorstore.
    Supported formats: .pdf, .txt, .md, .docx, .csv, .json
    """
    ext = os.path.splitext(path)[1].lower()
    full_text = ""
    
    try:
        if ext == '.pdf':
            full_text = _load_pdf(path)
        elif ext in ['.txt', '.md']:
            full_text = _load_text(path)
        elif ext == '.docx':
            full_text = _load_docx(path)
        elif ext in ['.csv', '.json']:
            full_text = _load_structured(path, ext)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        if not full_text.strip():
            print(f"Warning: No text extracted from {path}")
            return 0

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_text(full_text)
        
        if chunks:
            create_vectorstore(chunks)
            
        return len(chunks)
        
    except Exception as e:
        print(f"Error ingesting file {path}: {str(e)}")
        raise e

def _load_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def _load_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def _load_docx(path: str) -> str:
    doc = DocxDocument(path)
    return "\n".join([para.text for para in doc.paragraphs])

def _load_structured(path: str, ext: str) -> str:
    """Load CSV or JSON and convert to string representation"""
    text = ""
    if ext == '.csv':
        df = pd.read_csv(path)
        # Convert each row to a readable string format
        text = df.to_string(index=False)
    elif ext == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = json.dumps(data, indent=2)
    return text
