from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_classic.chains import RetrievalQA
from langchain_classic.callbacks.base import BaseCallbackHandler
from app.vectorstore import get_hybrid_retriever
import os,time
from queue import Queue, Empty
from threading import Thread
import json


class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for streaming LLM responses"""
    
    def __init__(self, queue: Queue):
        self.queue = queue
        self.tokens = []
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when LLM generates a new token"""
        self.queue.put({"type": "token", "content": token})
        self.tokens.append(token)
    
    def on_llm_end(self, *args, **kwargs) -> None:
        """Called when LLM finishes generating"""
        self.queue.put({"type": "end", "content": None})
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called when LLM encounters an error"""
        self.queue.put({"type": "error", "content": str(error)})





def ask_question_streaming(question: str):
    """Word-by-word streaming (FIXED VERSION)"""
    
    try:
        retriever = get_hybrid_retriever(k=3)
        
        if retriever is None:
            yield {"type": "error", "content": "No documents ingested yet."}
            yield {"type": "end", "content": None}
            return
        
        # Get complete answer
        model = HuggingFaceEndpoint(
            repo_id="HuggingFaceH4/zephyr-7b-beta",
            task="conversational",
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            temperature=0.2,
            max_new_tokens=512,
            top_p=0.95,
            repetition_penalty=1.15,
        )
        
        chat = ChatHuggingFace(llm=model, verbose=False)
        qa = RetrievalQA.from_chain_type(
            llm=chat,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False
        )
        
        result = qa.invoke({"query": question})
        answer = (result.get("answer") or result.get("result")) if isinstance(result, dict) else str(result)
        
        # Stream word by word
        words = answer.split()
        for i, word in enumerate(words):
            if i > 0:
                yield {"type": "token", "content": " "}
            yield {"type": "token", "content": word}
            time.sleep(0.05)  # Adjust speed here (0.05 = 50ms)
        
        yield {"type": "end", "content": None}
        
    except Exception as e:
        yield {"type": "error", "content": str(e)}
        yield {"type": "end", "content": None}