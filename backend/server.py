from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from profile_agent import ProfileAgent


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Chat Models
class ChatMessage(BaseModel):
    session_id: str
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    session_id: str
    message: str
    confidence_scores: Optional[Dict[str, float]] = {}
    summary_status: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = {}

class SessionCreate(BaseModel):
    user_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    created_at: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Chat Endpoints
@api_router.post("/chat/session", response_model=SessionResponse)
async def create_chat_session(input: SessionCreate):
    """Create a new chat session for profile building"""
    session_id = str(uuid.uuid4())
    session_data = {
        "session_id": session_id,
        "user_id": input.user_id or "anonymous",
        "profile_data": {},
        "confidence_scores": {},
        "conversation_history": [],
        "profile_summary": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.profile_sessions.insert_one(session_data)
    
    return SessionResponse(
        session_id=session_id,
        created_at=session_data["created_at"]
    )

@api_router.post("/chat/message", response_model=ChatResponse)
async def send_chat_message(input: ChatMessage):
    """Send a message to the ProfileAgent and get a response"""
    try:
        # Initialize ProfileAgent
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")
        
        agent = ProfileAgent(db=db, api_key=api_key)
        
        # Process the message
        result = await agent.process_message(
            session_id=input.session_id,
            user_message=input.message,
            conversation_history=input.conversation_history or []
        )
        
        return ChatResponse(
            session_id=input.session_id,
            message=result["message"],
            confidence_scores=result.get("confidence_scores", {}),
            summary_status=result.get("summary_status"),
            profile_data=result.get("profile_data", {})
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/session/{session_id}")
async def get_chat_session(session_id: str):
    """Retrieve session summary for MatchingAgent"""
    session = await db.profile_sessions.find_one({"session_id": session_id}, {"_id": 0})
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()