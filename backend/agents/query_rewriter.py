"""
Conditional Query Rewriter
Rewrites vague or ambiguous queries to improve retrieval quality.
"""

import logging

from config.llm import create_chat
from config.constants import QUERY_REWRITE

logger = logging.getLogger(__name__)


def _assess_query_clarity(query: str) -> float:
    """Heuristic clarity score (0-1). Lower means more vague."""
    words = query.strip().split()
    word_count = len(words)
    score = 1.0

    if word_count <= QUERY_REWRITE["min_word_count"]:
        score -= 0.3

    query_lower = query.lower()
    vague_hits = sum(1 for v in QUERY_REWRITE["vague_indicators"] if v in query_lower)
    if vague_hits > 0:
        score -= min(0.15 * vague_hits, 0.4)

    if word_count <= 3:
        score -= 0.2

    specific_terms = [
        "vpn", "okta", "mfa", "wifi", "slack", "outlook",
        "password", "email", "ticket", "laptop", "screen",
    ]
    if any(t in query_lower for t in specific_terms):
        score += 0.15

    return max(0.0, min(1.0, score))


def should_rewrite(query: str) -> bool:
    """Determine whether a query needs rewriting."""
    words = query.strip().split()
    if len(words) > QUERY_REWRITE["max_word_count"]:
        return False
    return _assess_query_clarity(query) < QUERY_REWRITE["clarity_threshold"]


async def rewrite_query(query: str) -> dict:
    """Conditionally rewrite a query for better retrieval."""
    if not should_rewrite(query):
        return {
            "original_query": query,
            "rewritten_query": query,
            "query_rewritten": False,
        }

    try:
        chat = create_chat(
            "rewrite",
            (
                "You are a query rewriting assistant for an IT support knowledge base. "
                "Rewrite the user's query to be more specific and detailed for better "
                "document retrieval. Preserve the original intent. Add relevant technical "
                "context where possible.\n\n"
                "Rules:\n"
                "- Output ONLY the rewritten query, nothing else\n"
                "- Keep it concise (1-2 sentences)\n"
                "- Add likely technical context\n"
                "- Do not invent new topics, only clarify the existing one"
            ),
        )
        rewritten = await chat.send_message(f"Rewrite this IT support query:\n{query}")
        rewritten = rewritten.strip().strip('"').strip("'")

        logger.info(f"Query rewritten: '{query[:50]}' -> '{rewritten[:50]}'")
        return {
            "original_query": query,
            "rewritten_query": rewritten,
            "query_rewritten": True,
        }
    except Exception as e:
        logger.error(f"Query rewrite failed: {e}")
        return {
            "original_query": query,
            "rewritten_query": query,
            "query_rewritten": False,
        }
