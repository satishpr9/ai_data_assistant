from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from dotenv import load_dotenv

load_dotenv(override=True)
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import shutil
import json
from typing import Optional
from datetime import timedelta, datetime
from app.database import get_db, init_db, User, Conversation, Message
from app.auth import (
    hash_password, 
    verify_password, 
    create_access_token, 
    get_current_user,
    get_current_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas import (
    UserCreate, 
    UserLogin, 
    Token, 
    UserResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    MessageResponse,
    QueryRequest
)
from app.ingest import ingest_file
from app.sql_ingest import ingest_business_data
from app.intent import is_chart_query, is_aggregation_query
from app.router import handle_chart_query
from app.analytics import top_customer
from app.rag_stream import ask_question_streaming

# LangChain Caching
from langchain_classic.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
import os

app = FastAPI(title="AI Data Assistant")

# Initialize database
init_db()

# Initialize LLM Cache
if not os.path.exists(".cache.db"):
    print("Creating new LLM cache database...")
set_llm_cache(SQLiteCache(database_path=".cache.db"))

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== AUTH ENDPOINTS ====================

@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user (default role is 'user')
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="user" 
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token (include role in payload if needed, but we fetch from DB)
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@app.post("/auth/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Include role in token
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# ...

@app.post("/ingest/mysql")
def ingest_mysql(current_user: User = Depends(get_current_admin)):
    """Ingest MySQL data (admin only)"""
    
    rows = ingest_business_data()
    return {
        "status": "success",
        "rows_ingested": rows
    }


@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


# ==================== CONVERSATION ENDPOINTS ====================

@app.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for current user"""
    
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    # Add message count
    result = []
    for conv in conversations:
        conv_dict = {
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": len(conv.messages)
        }
        result.append(conv_dict)
    
    return result


@app.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    conv_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new conversation"""
    
    conversation = Conversation(
        user_id=current_user.id,
        title=conv_data.title
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "message_count": 0
    }


@app.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation with all messages"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = []

    for msg in conversation.messages:
        messages.append({
        "id": msg.id,
        "conversation_id": msg.conversation_id,
        "role": msg.role,
        "content": msg.content,
        "mode": msg.mode,
        "metadata": (
            json.loads(msg.meta)
            if msg.meta and isinstance(msg.meta, str)
            else msg.meta
        ),
        "created_at": msg.created_at,
    })

    return {
    "id": conversation.id,
    "title": conversation.title,
    "created_at": conversation.created_at,
    "updated_at": conversation.updated_at,
    "message_count": len(messages),
    "messages": messages,
}



@app.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted"}


@app.patch("/conversations/{conversation_id}/title")
def update_conversation_title(
    conversation_id: int,
    title: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation title"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.title = title
    conversation.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Title updated"}


# ==================== QUERY ENDPOINTS (WITH HISTORY) ====================

@app.post("/ask/stream")
async def ask_stream(
    request: QueryRequest,
    conversation_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Streaming query with conversation history"""
    
    query = request.query
    
    # Validate conversation if provided
    conversation = None
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Save user message
    if conversation:
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=query,
            mode="rag"
        )
        db.add(user_message)
        db.commit()
        conversation.updated_at = datetime.utcnow()
        db.commit()
    
    # Handle non-streaming queries
    if is_chart_query(query):
        chart_data = handle_chart_query(query)
        
        if conversation:
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content="",
                mode="chart",
                metadata=json.dumps(chart_data)
            )
            db.add(assistant_message)
            db.commit()
        
        return {"mode": "chart", "chart": chart_data}
    
    if is_aggregation_query(query):
        result = top_customer()
        
        if conversation:
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=result.get("answer", ""),
                mode="aggregation",
                metadata=json.dumps(result.get("sources", []))
            )
            db.add(assistant_message)
            db.commit()
        
        return {"mode": "aggregation", **result}
    
    # Stream RAG responses
    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'start', 'mode': 'rag'})}\n\n"
            
            collected_answer = ""
            
            for item in ask_question_streaming(query):
                yield f"data: {json.dumps(item)}\n\n"
                
                # Collect answer for saving
                if item["type"] == "token":
                    collected_answer += item["content"]
            
            # Save assistant message after streaming completes
            if conversation and collected_answer:
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=collected_answer,
                    mode="rag"
                )
                db.add(assistant_message)
                db.commit()
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield f"data: {json.dumps({'type': 'end', 'content': None})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


# ==================== FILE UPLOAD ====================

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload file (protected) - Supports PDF, TXT, MD, DOCX, CSV, JSON"""
    
    file_path = f"data/uploads/{current_user.id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    chunks = ingest_file(file_path)
    
    return {
        "message": "File submitted successfully",
        "chunks_created": chunks
    }


@app.post("/ingest/mysql")
def ingest_mysql(current_user: User = Depends(get_current_admin)):
    """Ingest MySQL data (admin only)"""
    
    rows = ingest_business_data()
    return {
        "status": "success",
        "rows_ingested": rows
    }


@app.get("/health")
def health():
    return {"status": "ok"}