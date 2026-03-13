"""
RAG Evaluation Pipeline
Measures retrieval accuracy, response groundedness, hallucination rate, and latency.
Runs test queries concurrently for faster completion.
"""

import time
import asyncio
import logging

logger = logging.getLogger(__name__)

TEST_QUERIES = [
    {
        "query": "How do I reset my Okta MFA?",
        "expected_intent": "knowledge_search",
        "expected_doc_ids": ["kb-002"],
        "expected_keywords": ["okta", "mfa", "reset"]
    },
    {
        "query": "My VPN is not connecting to the corporate network",
        "expected_intent": "troubleshooting",
        "expected_doc_ids": ["kb-001"],
        "expected_keywords": ["vpn", "connect", "restart"]
    },
    {
        "query": "My laptop WiFi is not working",
        "expected_intent": "troubleshooting",
        "expected_doc_ids": ["kb-003"],
        "expected_keywords": ["wifi", "network", "adapter"]
    },
    {
        "query": "Create a ticket for laptop screen repair",
        "expected_intent": "ticket_creation",
        "expected_doc_ids": ["kb-006"],
        "expected_keywords": ["ticket", "repair"]
    },
    {
        "query": "How do I get access to Slack?",
        "expected_intent": "knowledge_search",
        "expected_doc_ids": ["kb-004"],
        "expected_keywords": ["slack", "access"]
    },
    {
        "query": "I forgot my corporate password and I am locked out",
        "expected_intent": "troubleshooting",
        "expected_doc_ids": ["kb-005"],
        "expected_keywords": ["password", "reset"]
    },
    {
        "query": "How do I set up Outlook on my phone?",
        "expected_intent": "knowledge_search",
        "expected_doc_ids": ["kb-007"],
        "expected_keywords": ["outlook", "email", "mobile"]
    },
    {
        "query": "I need to install Visual Studio Code on my laptop",
        "expected_intent": "knowledge_search",
        "expected_doc_ids": ["kb-008"],
        "expected_keywords": ["software", "install"]
    }
]


async def _evaluate_single(test, vector_store, process_query):
    """Evaluate a single test query."""
    start = time.time()

    # Test retrieval (fast, no LLM)
    search_results = vector_store.search(test["query"], top_k=3)
    retrieved_ids = [r["document"]["id"] for r in search_results]
    retrieval_hit = any(eid in retrieved_ids for eid in test["expected_doc_ids"])

    retrieval_result = {
        "query": test["query"],
        "expected": test["expected_doc_ids"],
        "retrieved": retrieved_ids[:3],
        "hit": retrieval_hit,
        "top_score": search_results[0]["score"] if search_results else 0
    }

    # Test full pipeline (includes LLM calls)
    response = await process_query(test["query"], "eval@company.com")
    latency = time.time() - start

    # Check intent accuracy
    intent_correct = response.get("intent") == test["expected_intent"]
    intent_result = {
        "query": test["query"],
        "expected": test["expected_intent"],
        "predicted": response.get("intent"),
        "correct": intent_correct
    }

    # Check groundedness
    response_text = (response.get("response") or "").lower()
    keyword_matches = sum(1 for kw in test["expected_keywords"] if kw in response_text)
    grounded = keyword_matches >= len(test["expected_keywords"]) * 0.5
    groundedness_result = {
        "query": test["query"],
        "keyword_coverage": f"{keyword_matches}/{len(test['expected_keywords'])}",
        "grounded": grounded
    }

    latency_result = {"query": test["query"], "latency": round(latency, 2)}

    return {
        "retrieval": retrieval_result,
        "intent": intent_result,
        "groundedness": groundedness_result,
        "latency": latency_result,
        "retrieval_hit": retrieval_hit,
        "intent_correct": intent_correct,
        "grounded": grounded,
        "latency_value": latency
    }


async def run_evaluation():
    """Run the full evaluation pipeline with concurrent query execution."""
    from knowledge_base.vector_store import vector_store
    from agents.orchestrator import process_query

    # Run all test queries concurrently (2 at a time to avoid overwhelming LLM)
    semaphore = asyncio.Semaphore(2)

    async def run_with_semaphore(test):
        async with semaphore:
            return await _evaluate_single(test, vector_store, process_query)

    eval_results = await asyncio.gather(
        *[run_with_semaphore(test) for test in TEST_QUERIES]
    )

    # Aggregate results
    results = {
        "total_queries": len(TEST_QUERIES),
        "retrieval_results": [r["retrieval"] for r in eval_results],
        "intent_results": [r["intent"] for r in eval_results],
        "groundedness_results": [r["groundedness"] for r in eval_results],
        "latencies": [r["latency"] for r in eval_results],
        "summary": {}
    }

    retrieval_hits = sum(1 for r in eval_results if r["retrieval_hit"])
    intent_hits = sum(1 for r in eval_results if r["intent_correct"])
    grounded_count = sum(1 for r in eval_results if r["grounded"])
    total_latency = sum(r["latency_value"] for r in eval_results)
    total = len(TEST_QUERIES)

    results["summary"] = {
        "retrieval_accuracy": round((retrieval_hits / total) * 100, 1),
        "intent_accuracy": round((intent_hits / total) * 100, 1),
        "groundedness_rate": round((grounded_count / total) * 100, 1),
        "hallucination_rate": round(((total - grounded_count) / total) * 100, 1),
        "average_latency": round(total_latency / total, 2),
        "total_queries": total
    }

    logger.info(f"Evaluation complete: {results['summary']}")
    return results
