# Enterprise AI IT Support Assistant

A production-grade Agentic AI IT Support Assistant featuring **Retrieval Augmented Generation (RAG)**, semantic search, intent classification, agentic task orchestration, tool execution, and a **self-improving feedback loop system**.

---

## Architecture

- **Backend**: FastAPI (Python) with modular architecture
- **Frontend**: React + Tailwind CSS + shadcn/ui
- **Database**: MongoDB (conversations, messages, tickets, feedback logs)
- **LLM**: Model-agnostic via configurable provider/model (env vars)
- **Vector Store**: TF-IDF + cosine similarity (scikit-learn)
- **Agent Orchestration**: LangGraph-style state machine

---

## System Workflow

```
User Query
    -> Conditional Query Rewrite
    -> Intent Classification
    -> Retrieval / Tool Routing
        -> Knowledge Search Agent
        -> Troubleshooting Agent
        -> Ticket Creation Tool
    -> Response Generation
    -> Quality Evaluation (Groundedness)
    -> Safe Fallback Decision
    -> Return Response
    -> Feedback Logging
```

---

## Core Features

### 1. RAG-Based Knowledge Search
Semantic search across 8 IT documents (VPN, WiFi, Okta, Slack, Password, Hardware, Email, Software) using TF-IDF embeddings and cosine similarity.

### 2. Intent Classification
LLM-powered classification into `knowledge_search`, `troubleshooting`, or `ticket_creation` with keyword-based fallback.

### 3. Agentic Workflow (LangGraph-style)
Directed graph state machine with conditional routing, quality evaluation, and safe fallback nodes.

### 4. Tool Execution
Simulated tools for ticket creation (auto-categorization, priority assignment) and system health checks.

### 5. Evaluation Pipeline
Async evaluation of retrieval accuracy, intent accuracy, groundedness rate, hallucination rate, and latency across 8 test queries.

---

## Self-Improving RAG with Feedback Loops

This system implements a **continuous improvement loop** inspired by production AI assistants. Instead of static RAG, the system captures quality signals from every interaction and uses them to identify weaknesses and guide improvements.


### Quality Signals Captured

Every interaction is logged with:
- **Query rewriting decisions**: Whether the query was rewritten and the rewritten form
- **Retrieval confidence**: Cosine similarity score mapped to high/medium/low labels
- **Groundedness evaluation**: LLM-assessed score (0-1) with reasoning
- **User feedback**: Helpful / Not Helpful ratings
- **Latency**: End-to-end processing time
- **Action outcomes**: Tickets created, system checks performed

### How Weak Responses Are Detected

The system flags interactions as potential failures when any of these conditions are true:
- **Retrieval confidence is low** (top similarity score below threshold)
- **Response is ungrounded** (groundedness score < 0.4)
- **User marks response as "Not Helpful"**

### How Analysis Guides Improvement

The Failure Analysis Engine:
1. Aggregates failure patterns by intent and document category
2. Identifies knowledge base gaps (categories with high failure rates)
3. Generates prioritized, actionable recommendations:
   - Add missing documentation for specific categories
   - Increase retrieval `top_k` for better coverage
   - Implement hybrid retrieval (BM25 + vector search)
   - Add re-ranking stages
   - Improve document chunking strategies
   - Refine prompt templates for specific intents

### Components

| Module | Path | Purpose |
|--------|------|---------|
| Query Rewriter | `agents/query_rewriter.py` | Conditional LLM-based query expansion |
| Quality Evaluator | `agents/quality_evaluator.py` | Groundedness scoring with fallback |
| Feedback Logger | `feedback/feedback_logger.py` | MongoDB telemetry storage |
| Failure Analysis | `evaluation/feedback_analysis.py` | Pattern detection & recommendations |
| Config | `config/constants.py` | Tunable thresholds for all components |
| LLM Abstraction | `config/llm.py` | Model-agnostic LLM factory |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/login` | Simulated employee login |
| POST | `/api/chat` | Chat with AI assistant (full pipeline) |
| POST | `/api/feedback` | Submit user feedback (helpful/not_helpful) |
| GET | `/api/feedback/stats` | Aggregated operational metrics |
| GET | `/api/feedback/analysis` | Failure analysis with recommendations |
| GET | `/api/conversations` | List user conversations |
| GET | `/api/conversations/:id` | Get conversation with messages |
| POST | `/api/ticket` | Create support ticket directly |
| GET | `/api/tickets` | List user tickets |
| GET | `/api/health` | System health check |
| POST | `/api/evaluation/run` | Start RAG evaluation pipeline |
| GET | `/api/evaluation/status/:id` | Poll evaluation results |
| GET | `/api/knowledge-base` | List knowledge base documents |
| GET | `/api/knowledge-base/:id` | Get document details |

---

## Project Structure

```
backend/
  config/
    constants.py          # Tunable thresholds and LLM config
    llm.py               # Model-agnostic LLM abstraction
  agents/
    orchestrator.py       # LangGraph-style agent pipeline
    query_rewriter.py     # Conditional query rewriting
    quality_evaluator.py  # Groundedness evaluation
  knowledge_base/
    documents.py          # IT knowledge base (8 documents)
    vector_store.py       # TF-IDF vector search with confidence
  feedback/
    feedback_logger.py    # MongoDB interaction telemetry
  evaluation/
    evaluator.py          # RAG evaluation pipeline
    feedback_analysis.py  # Failure analysis engine
  tools/
    ticket_tool.py        # Ticket creation simulation
    system_check_tool.py  # System health check simulation
  server.py               # FastAPI application

frontend/
  src/
    pages/
      LoginPage.js
      ChatPage.js
      EvaluationPage.js
      FeedbackAnalysisPage.js
    components/
      ChatMessage.js       # Includes feedback buttons & quality badges
      ChatInput.js
```

---


## Setup

```bash
# Backend
pip install -r backend/requirements.txt
cd backend && uvicorn server:app --host 0.0.0.0 --port 8001

# Frontend
cd frontend && yarn install && yarn start
```

Environment variables required in `backend/.env`:
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
OPEN_API_KEY=<your-key>
LLM_PROVIDER=openai
LLM_MODEL=<your-model>
```
