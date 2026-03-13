"""
Configuration Constants for Self-Improving RAG System
Tunable thresholds and settings. Override via environment variables.
"""

import os


# --- LLM Configuration ---
LLM_CONFIG = {
    "provider": os.environ.get("LLM_PROVIDER", "openai"),
    "model": os.environ.get("LLM_MODEL", "gpt-4o"),
    "api_key_env": "OPENAI_API_KEY",
}

# --- Retrieval Confidence Thresholds ---
RETRIEVAL_CONFIDENCE = {
    "high_threshold": float(os.environ.get("RETRIEVAL_HIGH_THRESHOLD", "0.25")),
    "medium_threshold": float(os.environ.get("RETRIEVAL_MEDIUM_THRESHOLD", "0.12")),
    "top_k": int(os.environ.get("RETRIEVAL_TOP_K", "5")),
    "min_score": float(os.environ.get("RETRIEVAL_MIN_SCORE", "0.05")),
}

# --- Hybrid Search ---
HYBRID_SEARCH = {
    "enabled": os.environ.get("HYBRID_SEARCH_ENABLED", "true").lower() == "true",
    "vector_weight": float(os.environ.get("HYBRID_VECTOR_WEIGHT", "0.6")),
    "bm25_weight": float(os.environ.get("HYBRID_BM25_WEIGHT", "0.4")),
}

# --- Query Rewriting ---
QUERY_REWRITE = {
    "min_word_count": 4,
    "max_word_count": 30,
    "vague_indicators": [
        "broken", "not working", "help", "issue", "problem", "error",
        "fix", "how", "what", "can't", "cannot", "doesn't work",
    ],
    "clarity_threshold": 0.5,
}

# --- Groundedness Evaluation ---
GROUNDEDNESS = {
    "low_score_threshold": 0.4,
    "medium_score_threshold": 0.7,
}

# --- Safe Fallback ---
FALLBACK = {
    "trigger_confidence": "low",
    "trigger_groundedness": 0.4,
    "auto_ticket_intents": ["troubleshooting"],
    "urgency_keywords": [
        "urgent", "critical", "emergency", "down", "blocked",
        "not working", "broken", "failing", "can't connect",
        "cannot access", "locked out",
    ],
}
