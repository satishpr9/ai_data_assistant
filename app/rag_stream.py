from langchain_openai import ChatOpenAI
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_classic.callbacks.base import BaseCallbackHandler
from app.vectorstore import get_hybrid_retriever
import os, time
from queue import Queue, Empty
from threading import Thread

class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for streaming LLM responses"""
    
    def __init__(self, queue: Queue):
        self.queue = queue
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when LLM generates a new token"""
        self.queue.put({"type": "token", "content": token})
    
    def on_llm_end(self, *args, **kwargs) -> None:
        """Called when LLM finishes generating"""
        self.queue.put({"type": "end", "content": None})
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called when LLM encounters an error"""
        self.queue.put({"type": "error", "content": str(error)})

def ask_question_streaming(question: str):
    """
    Real Streaming RAG Query
    Uses ChatOpenAI with Hugging Face Router
    """
    print(f"DEBUG: ask_question_streaming called with: {question}") # DEBUG
    queue = Queue()
    
    try:
        print("DEBUG: Getting retriever...") # DEBUG
        retriever = get_hybrid_retriever(k=3)
        
        if not retriever:
            yield {"type": "error", "content": "No documents ingested yet."}
            yield {"type": "end", "content": None}
            return

        # Initialize LLM with Hugging Face Router
        llm = ChatOpenAI(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            openai_api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            openai_api_base="https://router.huggingface.co/v1",
            temperature=0.2,
            max_tokens=512,
            streaming=True,
            callbacks=[StreamingCallbackHandler(queue)]
        )

        # RAG Prompt Template
        prompt_template = """
        You are a helpful AI assistant. Use the following pieces of context to answer the question at the end.
        
        **Instructions:**
        1. Answer the question clearly and concisely.
        2. If the answer involves a process, break it down into **numbered steps**.
        3. Use **bold text** for key terms or important values.
        4. If the answer is not in the context, say "I don't have enough information to answer that based on the provided documents."

        Context:
        {context}

        Question: {question}

        Answer:
        """

        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=False
        )
        
        # Run the chain in a separate thread so we can yield tokens from the queue
        def run_chain():
            try:
                qa.invoke({"query": question})
            except Exception as e:
                queue.put({"type": "error", "content": str(e)})
                queue.put({"type": "end", "content": None})

        thread = Thread(target=run_chain)
        thread.start()
        
        # Yield tokens from the queue as they become available
        while True:
            try:
                # Wait for next token
                token = queue.get(timeout=60.0) # 60s timeout to prevent hanging
                
                if token['type'] == 'end':
                    yield {"type": "end", "content": None}
                    break
                
                if token['type'] == 'error':
                    yield token
                    break
                
                yield token
                
            except Empty:
                yield {"type": "error", "content": "Timeout waiting for response"}
                break
        
    except Exception as e:
        print(f"Error during streaming RAG: {e}")
        yield {"type": "error", "content": str(e)}
        yield {"type": "end", "content": None}