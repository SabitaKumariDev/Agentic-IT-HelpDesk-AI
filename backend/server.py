"""
Enterprise AI IT Support Assistant - FastAPI Backend
Exposes endpoints for chat, feedback, ticket creation, health checks, and evaluation.
"""

import os
import sys
import uuid
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, ConfigDict

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="Enterprise AI IT Support Assistant")
api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ─── Initialize Knowledge Base ───────────────────────────────────────────────
from knowledge_base.vector_store import vector_store
vector_store.index_documents()
logger.info(f"Knowledge base initialized with {vector_store.get_document_count()} documents")

# ─── Initialize Feedback Logger ──────────────────────────────────────────────
from feedback.feedback_logger import FeedbackLogger
feedback_logger = FeedbackLogger(db)


# ─── Pydantic Models ────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str

class LoginResponse(BaseModel):
    email: str
    name: str
    session_id: str

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    user_email: str

class SourceInfo(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    title: str
    source: str
    score: float

class QualitySignals(BaseModel):
    query_rewritten: bool = False
    rewritten_query: str = ""
    retrieval_score: float = 0.0
    retrieval_confidence_label: str = ""
    grounded: bool = True
    groundedness_score: float = 1.0
    groundedness_reasoning: str = ""

class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    message_id: str
    conversation_id: str
    response: str
    intent: Optional[str] = None
    sources: List[SourceInfo] = []
    actions: List[dict] = []
    ticket: Optional[dict] = None
    latency: float = 0
    quality: Optional[QualitySignals] = None

class FeedbackRequest(BaseModel):
    message_id: str
    feedback: str  # "helpful" or "not_helpful"

class ConversationCreate(BaseModel):
    user_email: str
    title: Optional[str] = "New Conversation"

class ConversationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    user_email: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0

class TicketCreate(BaseModel):
    issue_description: str
    user_email: str

class HealthResponse(BaseModel):
    status: str
    services: dict
    knowledge_base: dict


# ─── Auth Endpoints ──────────────────────────────────────────────────────────

@api_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    email = request.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")

    name = email.split("@")[0].replace(".", " ").title()
    session_id = str(uuid.uuid4())

    await db.users.update_one(
        {"email": email},
        {"$set": {"email": email, "name": name, "last_login": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return LoginResponse(email=email, name=name, session_id=session_id)


# ─── Chat Endpoints ─────────────────────────────────────────────────────────

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a user query through the agentic AI pipeline."""
    from agents.orchestrator import process_query

    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        await db.conversations.insert_one({
            "id": conversation_id,
            "user_email": request.user_email,
            "title": request.query[:60],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "message_count": 0,
        })

    user_msg_id = str(uuid.uuid4())
    await db.messages.insert_one({
        "id": user_msg_id,
        "conversation_id": conversation_id,
        "role": "user",
        "content": request.query,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    result = await process_query(request.query, request.user_email)

    ai_msg_id = str(uuid.uuid4())
    await db.messages.insert_one({
        "id": ai_msg_id,
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": result["response"],
        "intent": result["intent"],
        "sources": result["sources"],
        "actions": result["actions"],
        "ticket": result["ticket"],
        "latency": result["latency"],
        "quality": {
            "query_rewritten": result.get("query_rewritten", False),
            "rewritten_query": result.get("rewritten_query", ""),
            "retrieval_score": result.get("retrieval_score", 0.0),
            "retrieval_confidence_label": result.get("retrieval_confidence_label", ""),
            "grounded": result.get("grounded", True),
            "groundedness_score": result.get("groundedness_score", 1.0),
            "groundedness_reasoning": result.get("groundedness_reasoning", ""),
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    if result["ticket"]:
        ticket_doc = {**result["ticket"], "conversation_id": conversation_id}
        ticket_doc.pop("_id", None)
        await db.tickets.insert_one(ticket_doc)

    await db.conversations.update_one(
        {"id": conversation_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}, "$inc": {"message_count": 2}},
    )

    # Log feedback telemetry asynchronously
    try:
        await feedback_logger.log_interaction({
            "message_id": ai_msg_id,
            "session_id": conversation_id,
            "user_email": request.user_email,
            "original_query": result.get("original_query", request.query),
            "rewritten_query": result.get("rewritten_query", request.query),
            "query_rewritten": result.get("query_rewritten", False),
            "intent": result.get("intent", ""),
            "retrieved_documents": [
                {"id": s.get("id"), "title": s.get("title"), "source": s.get("source"), "score": s.get("score"), "category": s.get("category", "")}
                for s in result.get("sources", [])
            ],
            "retrieval_score": result.get("retrieval_score", 0.0),
            "retrieval_confidence_label": result.get("retrieval_confidence_label", ""),
            "response": result.get("response", ""),
            "grounded": result.get("grounded", True),
            "groundedness_score": result.get("groundedness_score", 1.0),
            "groundedness_reasoning": result.get("groundedness_reasoning", ""),
            "latency_ms": int(result.get("latency", 0) * 1000),
            "action_taken": ", ".join(a.get("type", "") for a in result.get("actions", [])),
            "ticket_created": result.get("ticket") is not None,
            "ticket_id": result["ticket"]["ticket_id"] if result.get("ticket") else None,
        })
    except Exception as e:
        logger.error(f"Failed to log feedback: {e}")

    return ChatResponse(
        message_id=ai_msg_id,
        conversation_id=conversation_id,
        response=result["response"],
        intent=result["intent"],
        sources=result["sources"],
        actions=result["actions"],
        ticket=result["ticket"],
        latency=result["latency"],
        quality=QualitySignals(
            query_rewritten=result.get("query_rewritten", False),
            rewritten_query=result.get("rewritten_query", ""),
            retrieval_score=result.get("retrieval_score", 0.0),
            retrieval_confidence_label=result.get("retrieval_confidence_label", ""),
            grounded=result.get("grounded", True),
            groundedness_score=result.get("groundedness_score", 1.0),
            groundedness_reasoning=result.get("groundedness_reasoning", ""),
        ),
    )


# ─── Feedback Endpoints ─────────────────────────────────────────────────────

@api_router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback (helpful/not_helpful) for a response."""
    if request.feedback not in ("helpful", "not_helpful"):
        raise HTTPException(status_code=400, detail="Feedback must be 'helpful' or 'not_helpful'")
    success = await feedback_logger.update_user_feedback(request.message_id, request.feedback)
    if not success:
        raise HTTPException(status_code=404, detail="Feedback record not found")
    return {"status": "ok", "message_id": request.message_id, "feedback": request.feedback}


@api_router.get("/feedback/stats")
async def get_feedback_stats():
    """Get aggregated feedback statistics."""
    return await feedback_logger.get_stats()


@api_router.get("/feedback/analysis")
async def get_feedback_analysis():
    """Run failure analysis on feedback logs and return recommendations."""
    from evaluation.feedback_analysis import run_failure_analysis
    return await run_failure_analysis(feedback_logger)


# ─── Conversation Endpoints ─────────────────────────────────────────────────

@api_router.get("/conversations")
async def get_conversations(user_email: str):
    conversations = await db.conversations.find(
        {"user_email": user_email}, {"_id": 0}
    ).sort("updated_at", -1).to_list(50)
    return conversations


@api_router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    conversation = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = await db.messages.find(
        {"conversation_id": conversation_id}, {"_id": 0}
    ).sort("created_at", 1).to_list(200)
    return {"conversation": conversation, "messages": messages}


@api_router.post("/conversations")
async def create_conversation(request: ConversationCreate):
    conv_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": conv_id,
        "user_email": request.user_email,
        "title": request.title,
        "created_at": now,
        "updated_at": now,
        "message_count": 0,
    }
    await db.conversations.insert_one(doc)
    doc.pop("_id", None)
    return doc


# ─── Ticket Endpoints ───────────────────────────────────────────────────────

@api_router.post("/ticket")
async def create_ticket_endpoint(request: TicketCreate):
    from tools.ticket_tool import create_ticket
    ticket = await create_ticket(request.issue_description, request.user_email)
    await db.tickets.insert_one({**ticket})
    return ticket


@api_router.get("/tickets")
async def get_tickets(user_email: str):
    tickets = await db.tickets.find(
        {"created_by": user_email}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return tickets


# ─── Health Endpoint ─────────────────────────────────────────────────────────

@api_router.get("/health", response_model=HealthResponse)
async def health_check():
    from tools.system_check_tool import simulate_system_check
    from config.constants import HYBRID_SEARCH
    db_status = "connected"
    try:
        await db.command("ping")
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        services={
            "database": db_status,
            "llm": "configured" if os.environ.get("OPENAI_API_KEY") else "not_configured",
            "vector_store": "indexed" if vector_store.is_indexed else "not_indexed",
            "hybrid_search": "enabled" if HYBRID_SEARCH["enabled"] else "disabled",
        },
        knowledge_base={
            "document_count": vector_store.get_document_count(),
            "indexed": vector_store.is_indexed,
        },
    )


# ─── Evaluation Endpoint (Async with Polling) ───────────────────────────────

_eval_tasks = {}

@api_router.post("/evaluation/run")
async def start_evaluation():
    task_id = str(uuid.uuid4())
    _eval_tasks[task_id] = {"status": "running", "results": None}

    async def _run():
        try:
            from evaluation.evaluator import run_evaluation as evaluate
            results = await evaluate()
            _eval_tasks[task_id] = {"status": "completed", "results": results}
        except Exception as e:
            _eval_tasks[task_id] = {"status": "error", "results": None, "error": str(e)}

    asyncio.create_task(_run())
    return {"task_id": task_id, "status": "running"}


@api_router.get("/evaluation/status/{task_id}")
async def get_evaluation_status(task_id: str):
    task = _eval_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ─── Knowledge Base Endpoint ─────────────────────────────────────────────────

@api_router.get("/knowledge-base")
async def get_knowledge_base():
    from knowledge_base.documents import IT_KNOWLEDGE_BASE
    return [
        {
            "id": doc["id"],
            "title": doc["title"],
            "category": doc["category"],
            "tags": doc["tags"],
            "source": doc["source"],
            "last_updated": doc["last_updated"],
        }
        for doc in IT_KNOWLEDGE_BASE
    ]


@api_router.get("/knowledge-base/search-by-title")
async def get_knowledge_base_by_title(title: str):
    from knowledge_base.documents import IT_KNOWLEDGE_BASE
    title_lower = title.lower().strip()
    for doc in IT_KNOWLEDGE_BASE:
        if doc["title"].lower() == title_lower:
            return {
                "id": doc["id"],
                "title": doc["title"],
                "category": doc["category"],
                "tags": doc["tags"],
                "content": doc["content"],
                "source": doc["source"],
                "last_updated": doc["last_updated"],
            }
    raise HTTPException(status_code=404, detail="Document not found")


@api_router.get("/knowledge-base/{doc_id}")
async def get_knowledge_base_document(doc_id: str):
    from knowledge_base.documents import IT_KNOWLEDGE_BASE
    for doc in IT_KNOWLEDGE_BASE:
        if doc["id"] == doc_id:
            return {
                "id": doc["id"],
                "title": doc["title"],
                "category": doc["category"],
                "tags": doc["tags"],
                "content": doc["content"],
                "source": doc["source"],
                "last_updated": doc["last_updated"],
            }
    raise HTTPException(status_code=404, detail="Document not found")


# ─── App Configuration ──────────────────────────────────────────────────────

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
