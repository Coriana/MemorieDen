# main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import User, Session as SessionModel, Memory, History
import uuid

app = FastAPI(title="Mem0 Local API")

# Initialize the database
init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class AddMemoryRequest(BaseModel):
    content: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict] = None  # This can stay as 'metadata' for API clarity

class AddMemoryResponse(BaseModel):
    memory_id: str
    status: str

class UpdateMemoryRequest(BaseModel):
    memory_id: str
    new_content: str

class UpdateMemoryResponse(BaseModel):
    memory_id: str
    status: str

class MemoryResponse(BaseModel):
    memory_id: str
    content: str
    metadata: Optional[Dict] = None  # This will map to 'meta' in the database
    score: Optional[float] = None

class GetAllMemoriesResponse(BaseModel):
    memories: List[MemoryResponse]

class HistoryResponse(BaseModel):
    history: List[Dict]

# Helper Functions
def get_or_create_user(db: Session, user_id: str):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        user = User(user_id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def get_or_create_agent(db: Session, agent_id: str):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        agent = Agent(agent_id=agent_id)
        db.add(agent)
        db.commit()
        db.refresh(agent)
    return agent

def get_or_create_session(db: Session, session_id: str, user: Optional[User], agent: Optional[Agent]):
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        session = SessionModel(session_id=session_id, user_id=user.id if user else None, agent_id=agent.id if agent else None)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session

# API Endpoints

@app.post("/memories/add", response_model=AddMemoryResponse)
def add_memory(request: AddMemoryRequest, db: Session = Depends(get_db)):
    memory_id = f"mem_{uuid.uuid4().hex[:8]}"
    
    user = get_or_create_user(db, request.user_id) if request.user_id else None
    agent = get_or_create_agent(db, request.agent_id) if request.agent_id else None
    session = get_or_create_session(db, request.session_id, user, agent) if request.session_id else None
    
    memory = Memory(
        memory_id=memory_id,
        user_id=user.id if user else None,
        agent_id=agent.id if agent else None,
        session_id=session.id if session else None,
        content=request.content,
        meta=request.metadata  # Updated to 'meta'
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    
    return AddMemoryResponse(memory_id=memory_id, status="success")

@app.put("/memories/update", response_model=UpdateMemoryResponse)
def update_memory(request: UpdateMemoryRequest, db: Session = Depends(get_db)):
    memory = db.query(Memory).filter(Memory.memory_id == request.memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # Save history
    history = History(
        memory_id=memory.id,
        prev_value=memory.content,
        new_value=request.new_content
    )
    db.add(history)
    
    # Update memory
    memory.content = request.new_content
    db.commit()
    db.refresh(memory)
    
    return UpdateMemoryResponse(memory_id=request.memory_id, status="updated")

@app.get("/memories/search", response_model=GetAllMemoriesResponse)
def search_memories(query: str, user_id: Optional[str] = None, db: Session = Depends(get_db)):
    # Simple search implementation: SQL LIKE
    memories_query = db.query(Memory).filter(Memory.content.contains(query))
    
    if user_id:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return GetAllMemoriesResponse(memories=[])
        memories_query = memories_query.filter(Memory.user_id == user.id)
    
    memories = memories_query.all()
    
    # Placeholder for scoring (e.g., relevance, importance, recency)
    response_memories = [
        MemoryResponse(
            memory_id=mem.memory_id,
            content=mem.content,
            metadata=mem.meta,  # Updated to 'meta'
            score=1.0  # Simplified score
        )
        for mem in memories
    ]
    
    return GetAllMemoriesResponse(memories=response_memories)

@app.get("/memories/all", response_model=GetAllMemoriesResponse)
def get_all_memories(user_id: Optional[str] = None, agent_id: Optional[str] = None, session_id: Optional[str] = None, db: Session = Depends(get_db)):
    memories_query = db.query(Memory)
    
    if user_id:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            memories_query = memories_query.filter(Memory.user_id == user.id)
    
    if agent_id:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if agent:
            memories_query = memories_query.filter(Memory.agent_id == agent.id)
    
    if session_id:
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if session:
            memories_query = memories_query.filter(Memory.session_id == session.id)
    
    memories = memories_query.all()
    
    response_memories = [
        MemoryResponse(
            memory_id=mem.memory_id,
            content=mem.content,
            metadata=mem.meta  # Updated to 'meta'
        )
        for mem in memories
    ]
    
    return GetAllMemoriesResponse(memories=response_memories)

@app.get("/memories/history/{memory_id}", response_model=HistoryResponse)
def get_memory_history(memory_id: str, db: Session = Depends(get_db)):
    memory = db.query(Memory).filter(Memory.memory_id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    history_records = db.query(History).filter(History.memory_id == memory.id).order_by(History.updated_at.desc()).all()
    
    response_history = [
        {
            "prev_value": record.prev_value,
            "new_value": record.new_value,
            "updated_at": record.updated_at
        }
        for record in history_records
    ]
    
    return HistoryResponse(history=response_history)
