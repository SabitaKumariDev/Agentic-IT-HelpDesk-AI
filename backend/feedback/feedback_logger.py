"""
Feedback Logger
Stores rich interaction telemetry in MongoDB for analysis and improvement.
Decoupled from specific use cases - reusable for any RAG application.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


class FeedbackLogger:
    """Logs interaction data to MongoDB for continuous improvement."""

    def __init__(self, db):
        self.collection = db["feedback_logs"]

    async def log_interaction(self, data: dict) -> str:
        """Log a complete interaction record. Returns the message_id used as key."""
        record = {
            "message_id": data.get("message_id", ""),
            "session_id": data.get("session_id", ""),
            "user_email": data.get("user_email", ""),
            "timestamp": data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "original_query": data.get("original_query", ""),
            "rewritten_query": data.get("rewritten_query", ""),
            "query_rewritten": data.get("query_rewritten", False),
            "intent": data.get("intent", ""),
            "retrieved_documents": data.get("retrieved_documents", []),
            "retrieval_score": data.get("retrieval_score", 0.0),
            "retrieval_confidence_label": data.get("retrieval_confidence_label", ""),
            "response": data.get("response", ""),
            "grounded": data.get("grounded", True),
            "groundedness_score": data.get("groundedness_score", 0.0),
            "groundedness_reasoning": data.get("groundedness_reasoning", ""),
            "latency_ms": data.get("latency_ms", 0),
            "user_feedback": data.get("user_feedback"),
            "action_taken": data.get("action_taken", ""),
            "ticket_created": data.get("ticket_created", False),
            "ticket_id": data.get("ticket_id"),
        }
        await self.collection.insert_one(record)
        logger.info(f"Feedback logged for message_id={record['message_id']}")
        return record["message_id"]

    async def update_user_feedback(self, message_id: str, feedback: str) -> bool:
        """Update user feedback for an existing interaction record."""
        result = await self.collection.update_one(
            {"message_id": message_id},
            {
                "$set": {
                    "user_feedback": feedback,
                    "feedback_at": datetime.now(timezone.utc).isoformat(),
                }
            },
        )
        if result.modified_count == 0:
            logger.warning(f"No feedback record found for message_id={message_id}")
            return False
        return True

    async def get_all_logs(self, limit: int = 500) -> list:
        """Retrieve feedback logs for analysis."""
        return await self.collection.find({}, {"_id": 0}).sort(
            "timestamp", -1
        ).to_list(limit)

    async def get_stats(self) -> dict:
        """Compute aggregated feedback statistics."""
        total = await self.collection.count_documents({})
        if total == 0:
            return self._empty_stats()

        helpful = await self.collection.count_documents({"user_feedback": "helpful"})
        not_helpful = await self.collection.count_documents({"user_feedback": "not_helpful"})
        no_feedback = await self.collection.count_documents({"user_feedback": None})
        low_conf = await self.collection.count_documents({"retrieval_confidence_label": "low"})
        med_conf = await self.collection.count_documents({"retrieval_confidence_label": "medium"})
        ungrounded = await self.collection.count_documents({"grounded": False})
        rewritten = await self.collection.count_documents({"query_rewritten": True})
        tickets = await self.collection.count_documents({"ticket_created": True})

        pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$latency_ms"}}}]
        agg = await self.collection.aggregate(pipeline).to_list(1)
        avg_latency = round(agg[0]["avg"], 0) if agg and agg[0].get("avg") else 0

        feedback_total = helpful + not_helpful

        return {
            "total_interactions": total,
            "helpful_count": helpful,
            "not_helpful_count": not_helpful,
            "no_feedback_count": no_feedback,
            "helpful_rate": round(helpful / feedback_total * 100, 1) if feedback_total else 0,
            "not_helpful_rate": round(not_helpful / feedback_total * 100, 1) if feedback_total else 0,
            "low_confidence_count": low_conf,
            "medium_confidence_count": med_conf,
            "low_confidence_rate": round(low_conf / total * 100, 1),
            "ungrounded_count": ungrounded,
            "ungrounded_rate": round(ungrounded / total * 100, 1),
            "average_latency_ms": avg_latency,
            "query_rewrite_count": rewritten,
            "query_rewrite_rate": round(rewritten / total * 100, 1),
            "ticket_creation_count": tickets,
        }

    @staticmethod
    def _empty_stats() -> dict:
        return {
            "total_interactions": 0,
            "helpful_count": 0,
            "not_helpful_count": 0,
            "no_feedback_count": 0,
            "helpful_rate": 0,
            "not_helpful_rate": 0,
            "low_confidence_count": 0,
            "medium_confidence_count": 0,
            "low_confidence_rate": 0,
            "ungrounded_count": 0,
            "ungrounded_rate": 0,
            "average_latency_ms": 0,
            "query_rewrite_count": 0,
            "query_rewrite_rate": 0,
            "ticket_creation_count": 0,
        }
