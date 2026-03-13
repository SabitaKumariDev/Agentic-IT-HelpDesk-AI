"""
LangGraph-Style Agent Orchestrator
Implements a state-machine based agent workflow for IT support
with self-improving RAG capabilities.
"""

import os
import sys
import uuid
import time
import logging

sys.path.insert(0, str(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.llm import create_chat

from config.constants import FALLBACK, GROUNDEDNESS

logger = logging.getLogger(__name__)


# --- State ---

class AgentState:
    """State object passed through the agent graph nodes."""

    def __init__(self, query, user_email=""):
        self.original_query = query
        self.query = query
        self.rewritten_query = query
        self.query_rewritten = False
        self.user_email = user_email
        self.intent = None
        self.context = []
        self.response = ""
        self.sources = []
        self.actions = []
        self.ticket = None
        self.system_check = None
        self.latency = 0
        self.error = None
        # Quality signals
        self.retrieval_score = 0.0
        self.retrieval_confidence_label = ""
        self.grounded = True
        self.groundedness_score = 1.0
        self.groundedness_reasoning = ""


# --- Graph Infrastructure ---

class AgentNode:
    def __init__(self, name, func):
        self.name = name
        self.func = func


class AgentGraph:
    """LangGraph-style directed graph for agent orchestration."""

    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.conditional_edges = {}
        self.entry_point = None

    def add_node(self, name, func):
        self.nodes[name] = AgentNode(name, func)

    def add_edge(self, from_node, to_node):
        self.edges[from_node] = to_node

    def add_conditional_edge(self, from_node, condition_func):
        self.conditional_edges[from_node] = condition_func

    def set_entry_point(self, name):
        self.entry_point = name

    async def run(self, state):
        current = self.entry_point
        step = 0
        max_steps = 15

        while current and current != "__end__" and step < max_steps:
            step += 1
            node = self.nodes.get(current)
            if not node:
                break
            logger.info(f"[Step {step}] Executing node: {node.name}")
            state = await node.func(state)
            if current in self.conditional_edges:
                current = self.conditional_edges[current](state)
            elif current in self.edges:
                current = self.edges[current]
            else:
                break
        return state


# --- Node Functions ---

async def conditional_rewrite_node(state):
    """Conditionally rewrite vague queries to improve retrieval."""
    from agents.query_rewriter import rewrite_query

    result = await rewrite_query(state.original_query)
    state.rewritten_query = result["rewritten_query"]
    state.query_rewritten = result["query_rewritten"]
    if result["query_rewritten"]:
        state.query = result["rewritten_query"]
    return state


async def classify_intent_node(state):
    """Classify the user's intent using LLM."""
    try:
        chat = create_chat("intent", (
            "You are an IT support intent classifier. "
            "Classify the user query into exactly one of these intents:\n"
            "- knowledge_search: User is asking about IT procedures or how-to guides\n"
            "- troubleshooting: User is reporting a technical issue or problem\n"
            "- ticket_creation: User explicitly wants to create a support ticket\n\n"
            "Respond with ONLY the intent name, nothing else."
        ))
        response = await chat.send_message(f"Classify this query: {state.query}")
        intent = response.strip().lower().replace('"', '').replace("'", "")
        valid_intents = ["knowledge_search", "troubleshooting", "ticket_creation"]
        state.intent = intent if intent in valid_intents else "knowledge_search"
    except Exception as e:
        logger.error(f"Intent classification error: {e}")
        q = state.query.lower()
        if any(w in q for w in ["create ticket", "submit ticket", "report issue", "file a ticket"]):
            state.intent = "ticket_creation"
        elif any(w in q for w in ["not working", "broken", "issue", "problem", "error", "fail", "can't", "cannot"]):
            state.intent = "troubleshooting"
        else:
            state.intent = "knowledge_search"

    logger.info(f"Intent classified as: {state.intent}")
    return state


def route_by_intent(state):
    return {
        "knowledge_search": "knowledge_search",
        "troubleshooting": "troubleshooting",
        "ticket_creation": "ticket_creation",
    }.get(state.intent, "knowledge_search")


async def knowledge_search_node(state):
    """Search knowledge base and generate a grounded answer."""
    from knowledge_base.vector_store import vector_store
    from config.constants import RETRIEVAL_CONFIDENCE

    results = vector_store.search(state.query, top_k=RETRIEVAL_CONFIDENCE["top_k"])
    state.context = results
    state.sources = [
        {"id": r["document"]["id"], "title": r["title"], "source": r["source"], "score": r["score"], "category": r["document"].get("category", "")}
        for r in results
    ]

    confidence = vector_store.compute_confidence(results)
    state.retrieval_score = confidence["retrieval_score"]
    state.retrieval_confidence_label = confidence["retrieval_confidence_label"]

    context_text = "\n\n".join([
        f"Source: {r['title']} ({r['source']})\n{r['document']['content'][:1000]}"
        for r in results
    ])

    confidence_hint = ""
    if state.retrieval_confidence_label == "low":
        confidence_hint = (
            "\nIMPORTANT: Retrieval confidence is LOW. Be cautious and transparent. "
            "Indicate that information may be limited and suggest creating a support ticket if needed."
        )

    try:
        chat = create_chat("search", (
            "You are an enterprise IT support assistant. "
            "Answer the user's question based ONLY on the provided knowledge base context. "
            "Be concise, professional, and provide step-by-step instructions when appropriate. "
            "If the context does not contain relevant information, say so and suggest creating a support ticket. "
            "Always reference which source document you are using."
            + confidence_hint
        ))
        state.response = await chat.send_message(
            f"Knowledge Base Context:\n{context_text}\n\nUser Question: {state.query}"
        )
    except Exception as e:
        logger.error(f"Knowledge search LLM error: {e}")
        state.response = (
            "I found relevant documentation but encountered an error generating a response. "
            "Please try again or create a support ticket."
        )
        state.error = str(e)
    return state


async def troubleshooting_node(state):
    """Diagnose issues using knowledge base + system health checks."""
    from knowledge_base.vector_store import vector_store
    from tools.system_check_tool import simulate_system_check
    from config.constants import RETRIEVAL_CONFIDENCE

    results = vector_store.search(state.query, top_k=RETRIEVAL_CONFIDENCE["top_k"])
    state.context = results
    state.sources = [
        {"id": r["document"]["id"], "title": r["title"], "source": r["source"], "score": r["score"], "category": r["document"].get("category", "")}
        for r in results
    ]

    confidence = vector_store.compute_confidence(results)
    state.retrieval_score = confidence["retrieval_score"]
    state.retrieval_confidence_label = confidence["retrieval_confidence_label"]

    q = state.query.lower()
    service = "general"
    for keyword, svc in [("vpn", "vpn"), ("wifi", "wifi"), ("wireless", "wifi"),
                          ("email", "email"), ("outlook", "email"), ("slack", "slack"),
                          ("okta", "okta"), ("mfa", "okta"), ("password", "okta")]:
        if keyword in q:
            service = svc
            break

    check_result = simulate_system_check(service)
    state.system_check = check_result
    state.actions.append({
        "type": "system_check", "service": service, "result": check_result
    })

    context_text = "\n\n".join([
        f"Source: {r['title']} ({r['source']})\n{r['document']['content'][:1000]}"
        for r in results
    ])

    confidence_hint = ""
    if state.retrieval_confidence_label == "low":
        confidence_hint = (
            "\nIMPORTANT: Retrieval confidence is LOW. Be transparent about limitations."
        )

    try:
        chat = create_chat("troubleshoot", (
            "You are an enterprise IT support troubleshooting assistant. "
            "Diagnose the user's issue and provide step-by-step troubleshooting instructions.\n"
            "Use the provided knowledge base context and system check results.\n"
            "Structure your response as:\n"
            "1. Issue detected\n"
            "2. Possible causes\n"
            "3. Step-by-step troubleshooting steps\n"
            "4. If unresolved, recommend creating a support ticket\n\n"
            "Be professional and concise."
            + confidence_hint
        ))
        system_info = (
            f"\nSystem Check ({check_result['name']}): "
            f"Status={check_result['status']}, Details={check_result.get('details', 'N/A')}"
        )
        state.response = await chat.send_message(
            f"Context:\n{context_text}{system_info}\n\nUser Issue: {state.query}"
        )
    except Exception as e:
        logger.error(f"Troubleshooting LLM error: {e}")
        state.response = (
            "I identified your issue but encountered an error generating troubleshooting steps. "
            "Please try again or create a support ticket."
        )
        state.error = str(e)
    return state


async def ticket_creation_node(state):
    """Create a support ticket for the user's request."""
    from tools.ticket_tool import create_ticket

    ticket = await create_ticket(state.query, state.user_email)
    state.ticket = ticket
    state.actions.append({"type": "ticket_created", "ticket": ticket})

    try:
        chat = create_chat("ticket", (
            "You are an enterprise IT support assistant. "
            "A support ticket has been created. Confirm the ticket creation "
            "and provide a brief summary. Be professional and reassuring."
        ))
        state.response = await chat.send_message(
            f"User request: {state.query}\n\n"
            f"Ticket created: ID={ticket['ticket_id']}, "
            f"Category={ticket['category']}, Priority={ticket['priority']}, "
            f"Status={ticket['status']}, ETA={ticket['estimated_resolution']}"
        )
    except Exception as e:
        logger.error(f"Ticket creation LLM error: {e}")
        state.response = (
            f"Support ticket created successfully.\n\n"
            f"Ticket ID: {ticket['ticket_id']}\n"
            f"Category: {ticket['category']}\n"
            f"Priority: {ticket['priority']}\n"
            f"Status: {ticket['status']}\n"
            f"Estimated Resolution: {ticket['estimated_resolution']}\n\n"
            f"Our IT team will review your request shortly."
        )
    return state


async def quality_evaluation_node(state):
    """Evaluate response quality against retrieved documents."""
    from agents.quality_evaluator import evaluate_groundedness

    docs = [
        {"title": r.get("title", ""), "content": r.get("document", {}).get("content", "")}
        for r in state.context
    ]
    result = await evaluate_groundedness(state.response, docs)
    state.grounded = result["grounded"]
    state.groundedness_score = result["groundedness_score"]
    state.groundedness_reasoning = result["reasoning"]
    return state


async def safe_fallback_node(state):
    """Apply safe fallback behavior based on quality signals."""
    is_low_conf = state.retrieval_confidence_label == "low"
    is_ungrounded = state.groundedness_score < FALLBACK["trigger_groundedness"]
    q_lower = state.original_query.lower()
    is_urgent = any(kw in q_lower for kw in FALLBACK["urgency_keywords"])

    if is_low_conf and is_ungrounded:
        if state.intent in FALLBACK["auto_ticket_intents"]:
            from tools.ticket_tool import create_ticket
            ticket = await create_ticket(
                f"Auto-escalated: {state.original_query}", state.user_email
            )
            state.ticket = ticket
            state.actions.append({"type": "auto_escalated", "ticket": ticket})
            state.response += (
                f"\n\n---\n**Note:** I found limited documentation for this issue and cannot confidently "
                f"verify a resolution. A support ticket has been automatically created for follow-up.\n"
                f"**Ticket ID:** {ticket['ticket_id']} | **Priority:** {ticket['priority']} | "
                f"**ETA:** {ticket['estimated_resolution']}"
            )
        else:
            state.response += (
                "\n\n---\n**Note:** I found limited documentation relevant to this query "
                "and my confidence is low. If this doesn't resolve your issue, "
                "I recommend creating a support ticket for personalized assistance."
            )
    elif state.intent in FALLBACK["auto_ticket_intents"]:
        is_medium_conf = state.retrieval_confidence_label == "medium"
        should_escalate = is_urgent or is_medium_conf or is_ungrounded

        if should_escalate:
            from tools.ticket_tool import create_ticket
            ticket = await create_ticket(
                f"Auto-escalated: {state.original_query}", state.user_email
            )
            state.ticket = ticket
            state.actions.append({"type": "auto_escalated", "ticket": ticket})
            state.response += (
                f"\n\n---\n**Action taken:** A support ticket has been automatically created for follow-up.\n"
                f"**Ticket ID:** {ticket['ticket_id']} | **Priority:** {ticket['priority']} | "
                f"**ETA:** {ticket['estimated_resolution']}"
            )

    return state


# --- Build the Graph ---

def build_agent_graph():
    """Build the complete agent orchestration graph."""
    graph = AgentGraph()

    graph.add_node("conditional_rewrite", conditional_rewrite_node)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("knowledge_search", knowledge_search_node)
    graph.add_node("troubleshooting", troubleshooting_node)
    graph.add_node("ticket_creation", ticket_creation_node)
    graph.add_node("quality_evaluation", quality_evaluation_node)
    graph.add_node("safe_fallback", safe_fallback_node)

    graph.set_entry_point("conditional_rewrite")
    graph.add_edge("conditional_rewrite", "classify_intent")
    graph.add_conditional_edge("classify_intent", route_by_intent)

    graph.add_edge("knowledge_search", "quality_evaluation")
    graph.add_edge("troubleshooting", "quality_evaluation")
    graph.add_edge("quality_evaluation", "safe_fallback")
    graph.add_edge("safe_fallback", "__end__")
    graph.add_edge("ticket_creation", "__end__")

    return graph


agent_graph = build_agent_graph()


async def process_query(query, user_email=""):
    """Main entry point: process a user query through the agent pipeline."""
    start_time = time.time()
    state = AgentState(query, user_email)

    try:
        state = await agent_graph.run(state)
    except Exception as e:
        logger.error(f"Agent graph execution error: {e}")
        state.response = "I encountered an error processing your request. Please try again."
        state.error = str(e)

    state.latency = round(time.time() - start_time, 2)

    return {
        "response": state.response,
        "intent": state.intent,
        "sources": state.sources,
        "actions": state.actions,
        "ticket": state.ticket,
        "system_check": state.system_check,
        "latency": state.latency,
        "error": state.error,
        "original_query": state.original_query,
        "rewritten_query": state.rewritten_query,
        "query_rewritten": state.query_rewritten,
        "retrieval_score": state.retrieval_score,
        "retrieval_confidence_label": state.retrieval_confidence_label,
        "grounded": state.grounded,
        "groundedness_score": state.groundedness_score,
        "groundedness_reasoning": state.groundedness_reasoning,
    }
