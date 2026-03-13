"""
Groundedness Evaluator
Evaluates whether a generated response is grounded in retrieved documents.
"""

import json
import logging

from config.llm import create_chat
from config.constants import GROUNDEDNESS

logger = logging.getLogger(__name__)


async def evaluate_groundedness(response: str, retrieved_docs: list) -> dict:
    """Evaluate if the response is supported by the retrieved documents."""
    if not response or not retrieved_docs:
        return {
            "grounded": False,
            "groundedness_score": 0.0,
            "reasoning": "No response or no retrieved documents to evaluate against.",
        }

    doc_context = "\n\n".join(
        f"Document: {d.get('title', 'Untitled')}\n{d.get('content', '')[:800]}"
        for d in retrieved_docs
    )

    try:
        chat = create_chat(
            "groundedness",
            (
                "You are a response quality evaluator. Assess whether the given response "
                "is grounded in (supported by) the provided source documents.\n\n"
                "Respond with ONLY a valid JSON object (no markdown, no extra text):\n"
                "{\n"
                '  "grounded": true or false,\n'
                '  "groundedness_score": float between 0.0 and 1.0,\n'
                '  "reasoning": "brief explanation"\n'
                "}\n\n"
                "Scoring guide:\n"
                "- 0.9-1.0: Fully supported with accurate citations\n"
                "- 0.7-0.89: Mostly supported, minor extrapolations\n"
                "- 0.4-0.69: Partially supported, some claims lack evidence\n"
                "- 0.0-0.39: Mostly unsupported or hallucinated"
            ),
        )
        raw = await chat.send_message(
            f"Source Documents:\n{doc_context}\n\n---\nResponse to evaluate:\n{response}"
        )
        raw = raw.strip()

        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        result = json.loads(raw)
        score = max(0.0, min(1.0, float(result.get("groundedness_score", 0.0))))

        return {
            "grounded": result.get("grounded", score >= GROUNDEDNESS["low_score_threshold"]),
            "groundedness_score": round(score, 2),
            "reasoning": result.get("reasoning", "Evaluation completed."),
        }
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning(f"Groundedness JSON parse failed: {e}, using keyword fallback")
        return _keyword_fallback(response, retrieved_docs)
    except Exception as e:
        logger.error(f"Groundedness evaluation error: {e}")
        return _keyword_fallback(response, retrieved_docs)


def _keyword_fallback(response: str, retrieved_docs: list) -> dict:
    """Fallback groundedness check using keyword overlap."""
    if not retrieved_docs:
        return {
            "grounded": False,
            "groundedness_score": 0.0,
            "reasoning": "No documents available for comparison.",
        }

    doc_words = set()
    for doc in retrieved_docs:
        text = doc.get("content", "") + " " + doc.get("title", "")
        doc_words.update(w.lower() for w in text.split() if len(w) > 3)

    resp_words = [w.lower() for w in response.split() if len(w) > 3]
    if not resp_words:
        return {
            "grounded": False,
            "groundedness_score": 0.0,
            "reasoning": "Empty response.",
        }

    overlap = sum(1 for w in resp_words if w in doc_words)
    score = round(min(1.0, overlap / len(resp_words)), 2)

    return {
        "grounded": score >= GROUNDEDNESS["low_score_threshold"],
        "groundedness_score": score,
        "reasoning": (
            f"Keyword overlap: {overlap}/{len(resp_words)} content words "
            f"found in source documents."
        ),
    }
