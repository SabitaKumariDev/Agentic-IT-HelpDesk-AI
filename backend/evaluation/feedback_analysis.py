"""
Failure Analysis Engine
Analyzes feedback logs to identify patterns in poor responses
and generate actionable improvement recommendations.
Reusable for any RAG application.
"""

import logging
from collections import Counter

logger = logging.getLogger(__name__)

ILLUSTRATIVE_FAILURES = [
    {
        "query": "VPN broken after login issue",
        "confidence_label": "low",
        "groundedness": {"grounded": False, "score": 0.28, "reasoning": "Response included steps not present in knowledge base documents."},
        "user_feedback": "not_helpful",
        "recommended_fix": "Add documentation covering VPN issues specifically related to authentication and post-login failures. Current VPN doc focuses on general connectivity.",
    },
    {
        "query": "How do I set up Okta MFA on a new phone?",
        "confidence_label": "medium",
        "groundedness": {"grounded": True, "score": 0.55, "reasoning": "Partially grounded. MFA reset steps covered but device migration is not documented."},
        "user_feedback": "not_helpful",
        "recommended_fix": "Expand Okta MFA documentation to cover device migration scenarios (new phone setup, transferring authenticator). Consider adding a dedicated 'Device Change' section.",
    },
    {
        "query": "WiFi keeps dropping in conference rooms",
        "confidence_label": "low",
        "groundedness": {"grounded": False, "score": 0.32, "reasoning": "Response suggested generic WiFi troubleshooting but lacked location-specific guidance."},
        "user_feedback": "not_helpful",
        "recommended_fix": "Add location-aware troubleshooting content. Include conference room WiFi access points, known dead zones, and steps to report coverage issues to facilities.",
    },
]


async def run_failure_analysis(feedback_logger) -> dict:
    """Analyze feedback logs and produce actionable recommendations."""
    logs = await feedback_logger.get_all_logs(limit=1000)
    stats = await feedback_logger.get_stats()

    failures = [
        log for log in logs
        if log.get("user_feedback") == "not_helpful"
        or not log.get("grounded", True)
        or log.get("retrieval_confidence_label") == "low"
    ]

    intent_breakdown = Counter(f.get("intent", "unknown") for f in failures)
    category_counts = Counter()
    for f in failures:
        for doc in f.get("retrieved_documents", []):
            category_counts[doc.get("category", "unknown")] += 1

    query_rewrite_failures = [f for f in failures if f.get("query_rewritten")]

    recommendations = _generate_recommendations(stats, failures, intent_breakdown, category_counts)

    sample_failures = _extract_sample_failures(failures)
    if len(sample_failures) < 3:
        remaining = 3 - len(sample_failures)
        sample_failures.extend(ILLUSTRATIVE_FAILURES[:remaining])

    return {
        "stats": stats,
        "failure_count": len(failures),
        "total_logs": len(logs),
        "intent_failure_breakdown": dict(intent_breakdown),
        "category_failure_breakdown": dict(category_counts),
        "query_rewrite_failure_count": len(query_rewrite_failures),
        "recommendations": recommendations,
        "sample_failures": sample_failures,
    }


def _extract_sample_failures(failures: list) -> list:
    """Extract representative failure cases from real data."""
    samples = []
    for f in failures[:10]:
        samples.append({
            "query": f.get("original_query", f.get("rewritten_query", "")),
            "confidence_label": f.get("retrieval_confidence_label", "unknown"),
            "groundedness": {
                "grounded": f.get("grounded", False),
                "score": f.get("groundedness_score", 0),
                "reasoning": f.get("groundedness_reasoning", ""),
            },
            "user_feedback": f.get("user_feedback"),
            "recommended_fix": _suggest_fix_for_failure(f),
        })
        if len(samples) >= 5:
            break
    return samples


def _suggest_fix_for_failure(failure: dict) -> str:
    """Generate a fix suggestion for a single failure case."""
    reasons = []
    if failure.get("retrieval_confidence_label") == "low":
        reasons.append("Improve document coverage for this query category")
    if not failure.get("grounded", True):
        reasons.append("Add source documents that directly address this topic")
    if failure.get("user_feedback") == "not_helpful":
        reasons.append("Review and improve response generation prompts for this intent")
    if failure.get("query_rewritten") and failure.get("retrieval_confidence_label") in ("low", "medium"):
        reasons.append("Query rewriting did not improve retrieval - consider adding synonyms to knowledge base")
    return ". ".join(reasons) if reasons else "Review interaction for manual improvement opportunities."


def _generate_recommendations(stats: dict, failures: list, intent_counts: Counter, category_counts: Counter) -> list:
    """Generate prioritized, actionable recommendations."""
    recs = []
    total = stats.get("total_interactions", 0)
    if total == 0:
        return [{
            "category": "Data Collection",
            "action": "Collect more interaction data before analysis can be performed",
            "reason": "No interactions logged yet",
            "priority": "high",
        }]

    if stats.get("low_confidence_rate", 0) > 10:
        recs.append({
            "category": "Retrieval Quality",
            "action": "Increase retrieval top_k from 3 to 5 to capture more relevant documents",
            "reason": f"{stats['low_confidence_rate']}% of queries have low retrieval confidence",
            "priority": "high",
        })

    if stats.get("ungrounded_rate", 0) > 5:
        recs.append({
            "category": "Response Quality",
            "action": "Implement hybrid retrieval (BM25 + vector search) for better document matching",
            "reason": f"{stats['ungrounded_rate']}% of responses are flagged as ungrounded",
            "priority": "high",
        })

    if stats.get("not_helpful_rate", 0) > 20:
        recs.append({
            "category": "User Satisfaction",
            "action": "Review and improve response generation prompts, especially for frequently failing intents",
            "reason": f"{stats['not_helpful_rate']}% of rated responses marked not helpful",
            "priority": "high",
        })

    top_failing_cats = category_counts.most_common(3)
    for cat, count in top_failing_cats:
        recs.append({
            "category": "Knowledge Base Gap",
            "action": f"Add more documentation for '{cat}' category ({count} failures)",
            "reason": f"'{cat}' is a top failure category with {count} associated failures",
            "priority": "medium",
        })

    top_failing_intents = intent_counts.most_common(2)
    for intent, count in top_failing_intents:
        recs.append({
            "category": "Intent Handling",
            "action": f"Refine {intent} pipeline handling ({count} failures)",
            "reason": f"'{intent}' intent has {count} associated failures",
            "priority": "medium",
        })

    if stats.get("query_rewrite_rate", 0) > 30:
        recs.append({
            "category": "Query Understanding",
            "action": "Improve document chunking strategy to handle vague queries better",
            "reason": f"{stats['query_rewrite_rate']}% of queries required rewriting",
            "priority": "low",
        })

    if stats.get("average_latency_ms", 0) > 5000:
        recs.append({
            "category": "Performance",
            "action": "Optimize retrieval pipeline and consider caching frequent queries",
            "reason": f"Average latency is {stats['average_latency_ms']}ms, above 5s threshold",
            "priority": "medium",
        })

    recs.append({
        "category": "Advanced Retrieval",
        "action": "Add a re-ranking stage after initial retrieval to improve document relevance",
        "reason": "Re-ranking consistently improves RAG precision in production systems",
        "priority": "low",
    })

    if not recs:
        recs.append({
            "category": "System Health",
            "action": "System performing within acceptable parameters. Continue monitoring.",
            "reason": "No critical issues detected",
            "priority": "low",
        })

    return recs
