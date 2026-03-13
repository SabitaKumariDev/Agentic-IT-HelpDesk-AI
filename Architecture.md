# Agentic AI IT Support Assistant

---

## Overview

This system goes beyond a simple chatbot. It implements a **state-machine driven agent** that:

1. **Understands intent** — Classifies user queries into knowledge search, troubleshooting, or ticket creation
2. **Retrieves intelligently** — Uses hybrid search (TF-IDF cosine similarity + BM25 keyword matching) across a 12-document IT knowledge base
3. **Generates grounded responses** — Produces answers anchored to retrieved documents, with confidence and groundedness scoring
4. **Takes autonomous actions** — Runs system health checks, auto-creates support tickets for urgent issues
5. **Self-improves** — Collects user feedback, logs quality signals, and surfaces actionable recommendations through an analytics dashboard

---

## Key Features

1. **Agentic Orchestration**: LangGraph-style state machine with conditional routing across 7 graph nodes
2. **Hybrid Search**: TF-IDF cosine similarity (60%) + BM25 keyword matching (40%) for robust retrieval
3. **Conditional Query Rewriting**: Automatically rewrites vague queries (e.g., "VPN broken" -> "How to troubleshoot VPN connectivity issues")
4. **Retrieval Confidence Scoring**: Classifies retrieval quality as high/medium/low with tunable thresholds
5. **Groundedness Evaluation**: LLM-based check with keyword fallback to verify responses are supported by documents
6. **Safe Fallback Behavior**: Auto-escalates to support tickets when confidence is low + query is urgent
7. **User Feedback Loop**: Thumbs up/down on every response, logged with full interaction telemetry
8. **Failure Analysis Dashboard**: Real-time metrics, failure patterns, and AI-generated improvement recommendations
9. **RAG Evaluation Pipeline**: Automated test suite measuring retrieval accuracy, intent accuracy, and groundedness rate
10. **12-Document Knowledge Base**: Covers VPN, WiFi, Okta, Slack, Email, Passwords, Hardware, Software, Printers, Teams, OneDrive, Zoom

---

## System Architecture

```
                                   SYSTEM ARCHITECTURE
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                              FRONTEND (React)                              │
 │                                                                             │
 │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌────────────────────────┐  │
 │  │  Login   │  │   Chat   │  │  Evaluation  │  │  Feedback Analysis     │  │
 │  │   Page   │  │   Page   │  │    Page      │  │     Dashboard          │  │
 │  └──────────┘  └──────────┘  └──────────────┘  └────────────────────────┘  │
 │       │             │               │                     │                 │
 │       └─────────────┴───────────────┴─────────────────────┘                 │
 │                              │ Axios HTTP                                   │
 └──────────────────────────────┼──────────────────────────────────────────────┘
                                │
                       ┌────────▼────────┐
                       │   FastAPI API   │
                       │   (port 8001)   │
                       └────────┬────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
 ┌────────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
 │  Agent Pipeline  │  │  Feedback &     │  │  Evaluation     │
 │  (Orchestrator)  │  │  Analytics      │  │  Pipeline       │
 │                  │  │                  │  │                  │
 │  7 Graph Nodes   │  │  Logger +       │  │  8 Test Queries  │
 │  State Machine   │  │  Analyzer       │  │  Automated       │
 └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
          │                     │                     │
          ├─────────────────────┼─────────────────────┤
          │                     │                     │
 ┌────────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
 │   Vector Store   │  │    MongoDB      │  │   OpenAI API    │
 │  (TF-IDF + BM25) │  │  (4 collections)│  │   (GPT-4o)      │
 │  12 Documents    │  │                  │  │                  │
 └─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Agentic Pipeline — LangGraph-Style Orchestration

The core of the system is a **directed acyclic graph (DAG)** that routes each user query through a series of processing nodes. This is inspired by [LangGraph](https://github.com/langchain-ai/langgraph) but implemented from scratch without external dependencies.

```
                        AGENT GRAPH (7 Nodes)

                     ┌──────────────────────┐
                     │    User Query Input   │
                     └──────────┬───────────┘
                                │
                     ┌──────────▼───────────┐
                     │  1. Conditional       │  Heuristic clarity scoring
                     │     Query Rewrite     │  Rewrites if score < 0.5
                     └──────────┬───────────┘
                                │
                     ┌──────────▼───────────┐
                     │  2. Intent            │  LLM classification with
                     │     Classification    │  keyword fallback
                     └──────────┬───────────┘
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
      ┌──────────▼───┐  ┌──────▼──────┐  ┌───▼──────────┐
      │ 3. Knowledge │  │ 4. Trouble- │  │ 5. Ticket    │
      │    Search    │  │    shooting │  │    Creation  │──── END
      │              │  │             │  │              │
      │ Hybrid RAG + │  │ RAG + System│  │ Auto-classify│
      │ LLM Generate │  │ Health Check│  │ + priority   │
      └──────┬───────┘  └──────┬──────┘  └──────────────┘
             │                 │
             └────────┬────────┘
                      │
           ┌──────────▼───────────┐
           │  6. Quality          │  LLM groundedness check
           │     Evaluation       │  with keyword fallback
           └──────────┬───────────┘
                      │
           ┌──────────▼───────────┐
           │  7. Safe Fallback    │  Auto-escalation logic
           │     Decision         │  for low conf + urgency
           └──────────┬───────────┘
                      │
                     END
```



## Self-Improving RAG Architecture

The system implements a **closed-loop feedback cycle** that captures quality signals at every stage:

```
                    SELF-IMPROVING RAG LOOP

   ┌─────────────────────────────────────────────────┐
   │                                                   │
   │  ┌───────────┐    ┌────────────┐    ┌─────────┐  │
   │  │  Query     │───>│  Retrieval  │───>│  LLM    │  │
   │  │  Rewriter  │    │  (Hybrid)   │    │  Gen    │  │
   │  └───────────┘    └─────┬──────┘    └────┬────┘  │
   │                         │                 │       │
   │              ┌──────────▼─────────────────▼──┐    │
   │              │     Quality Evaluation         │    │
   │              │  - Retrieval Confidence         │    │
   │              │  - Groundedness Score           │    │
   │              │  - Latency Measurement          │    │
   │              └──────────┬─────────────────────┘    │
   │                         │                          │
   │              ┌──────────▼─────────────────────┐    │
   │              │     User Feedback               │    │
   │              │  - Helpful / Not Helpful         │    │
   │              └──────────┬─────────────────────┘    │
   │                         │                          │
   │              ┌──────────▼─────────────────────┐    │
   │              │     MongoDB Feedback Store       │    │
   │              │  - Full interaction telemetry    │    │
   │              └──────────┬─────────────────────┘    │
   │                         │                          │
   │              ┌──────────▼─────────────────────┐    │
   │              │     Failure Analysis Engine      │    │
   │              │  - Aggregate metrics             │    │
   │              │  - Identify failure patterns     │──┘
   │              │  - Generate recommendations      │
   │              └────────────────────────────────┘
   │
   │  Recommendations feed back into system tuning:
   │  - Adjust retrieval top_k, thresholds
   │  - Expand knowledge base for weak categories
   │  - Enable/disable hybrid search
   └──────────────────────────────────────────────────
```


## Hybrid Search Engine

The retrieval layer combines two complementary search algorithms for robust document matching:

```
                    HYBRID SEARCH PIPELINE

    User Query: "Teams meeting no sound"
                       │
         ┌─────────────┼─────────────┐
         │                           │
    ┌────▼────┐                 ┌────▼────┐
    │ TF-IDF  │                 │  BM25   │
    │ Cosine  │                 │ Okapi   │
    │Similarity│                │         │
    └────┬────┘                 └────┬────┘
         │                           │
    Semantic matching           Keyword matching
    via n-gram vectors          via term frequency
         │                           │
    ┌────▼────┐                 ┌────▼────┐
    │Normalize│                 │Normalize│
    │ [0, 1]  │                 │ [0, 1]  │
    └────┬────┘                 └────┬────┘
         │                           │
         └─────────┬─────────────────┘
                   │
           ┌───────▼───────┐
           │  Weighted Sum  │
           │  0.6 * TF-IDF  │
           │ + 0.4 * BM25   │
           └───────┬───────┘
                   │
           ┌───────▼───────┐
           │   Top-K (5)    │
           │   + Min Score   │
           │     Filter     │
           └───────┬───────┘
                   │
           ┌───────▼───────┐
           │  Confidence    │
           │  Scoring       │
           │                │
           │  >= 0.25: HIGH │
           │  >= 0.12: MED  │
           │  < 0.12: LOW   │
           └───────────────┘
```


## Database Architecture

### MongoDB Collections

```
                        DATABASE SCHEMA (MongoDB)

┌─────────────────────────────────────────────────────────────────┐
│                          MongoDB                                 │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  ┌──────────┐ │
│  │    users     │  │conversations│  │  messages  │  │ tickets  │ │
│  ├─────────────┤  ├─────────────┤  ├───────────┤  ├──────────┤ │
│  │ email    PK │  │ id       PK │  │ id     PK │  │ticket_id │ │
│  │ name       │  │ user_email  │──│ conv_id FK│  │ conv_id  │ │
│  │ last_login │  │ title       │  │ role      │  │ category │ │
│  └─────────────┘  │ created_at  │  │ content   │  │ priority │ │
│                    │ updated_at  │  │ intent    │  │ status   │ │
│  ┌─────────────┐  │ msg_count   │  │ sources[] │  │created_by│ │
│  │  feedback    │  └─────────────┘  │ actions[] │  │created_at│ │
│  ├─────────────┤                    │ ticket    │  └──────────┘ │
│  │ message_id  │                    │ quality{} │               │
│  │ session_id  │                    │ latency   │               │
│  │ user_email  │                    │created_at │               │
│  │ orig_query  │                    └───────────┘               │
│  │ rewritten_q │                                                 │
│  │ intent      │    Relationships:                               │
│  │ retrieval_  │    users.email ──< conversations.user_email     │
│  │   score     │    conversations.id ──< messages.conversation_id│
│  │ confidence  │    conversations.id ──< tickets.conversation_id │
│  │ grounded    │    messages.id ──< feedback.message_id          │
│  │ ground_score│                                                 │
│  │ ground_rsn  │                                                 │
│  │ response    │                                                 │
│  │ latency_ms  │                                                 │
│  │ user_feedbk │                                                 │
│  │ timestamp   │                                                 │
│  └─────────────┘                                                 │
└─────────────────────────────────────────────────────────────────┘
```


---

## Frontend Architecture

```
frontend/src/
├── pages/
│   ├── LoginPage.js              # Email-based authentication
│   ├── ChatPage.js               # Main chat interface + sidebar
│   ├── EvaluationPage.js         # RAG evaluation pipeline runner
│   └── FeedbackAnalysisPage.js   # Analytics dashboard
├── components/
│   ├── ChatMessage.js            # Message bubble with badges, sources, feedback
│   ├── ChatInput.js              # Input bar with send button
│   └── ui/                       # shadcn/ui component library (30+ components)
├── App.js                        # Router (react-router-dom)
├── index.js                      # Entry point
└── index.css                     # Tailwind CSS + custom animations
```


---

## Project Structure

```
agentic-it-helpdesk-ai/
│
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py        # LangGraph-style agent DAG (7 nodes)
│   │   ├── quality_evaluator.py   # Groundedness evaluation (LLM + fallback)
│   │   └── query_rewriter.py      # Conditional query rewriting
│   │
│   ├── config/
│   │   ├── constants.py           # All tunable parameters (thresholds, weights)
│   │   └── llm.py                 # OpenAI client abstraction
│   │
│   ├── evaluation/
│   │   ├── evaluator.py           # RAG pipeline evaluation (8 test queries)
│   │   └── feedback_analysis.py   # Metrics aggregation + recommendation engine
│   │
│   ├── feedback/
│   │   └── feedback_logger.py     # MongoDB telemetry logger
│   │
│   ├── knowledge_base/
│   │   ├── documents.py           # 12 IT knowledge base documents
│   │   └── vector_store.py        # Hybrid search engine (TF-IDF + BM25)
│   │
│   ├── tools/
│   │   ├── ticket_tool.py         # Auto-categorizing ticket creation
│   │   └── system_check_tool.py   # IT service health simulator
│   │
│   ├── server.py                  # FastAPI application + all endpoints
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── pages/                 # 4 page components
│   │   ├── components/            # Chat components + shadcn/ui library
│   │   ├── hooks/                 # Custom React hooks
│   │   └── lib/                   # Utility functions
│   ├── public/                    # Static assets
│   ├── package.json               # Node dependencies
│   └── .env                       # Frontend environment variables
│
└── README.md
```

---
