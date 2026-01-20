from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .vectorstore import create_vectorstore

def ingest_pdf(path: str) -> int:
    reader = PdfReader(path)
    full_text = ""

    for page in reader.pages:
        if page.extract_text():
            full_text += page.extract_text()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_text(full_text)
    create_vectorstore(chunks)

    return len(chunks)
