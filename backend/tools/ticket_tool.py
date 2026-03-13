"""
Ticket Creation Tool
Simulates IT service desk ticket creation with auto-categorization and priority assignment.
"""

import random
from datetime import datetime, timezone


async def create_ticket(issue_description, created_by=""):
    """Create a simulated IT support ticket with auto-categorization."""
    ticket_id = random.randint(1000, 9999)
    desc_lower = issue_description.lower()

    # Auto-determine priority
    priority = "medium"
    if any(w in desc_lower for w in ["urgent", "emergency", "critical", "broken", "down", "not working"]):
        priority = "high"
    elif any(w in desc_lower for w in ["question", "how to", "info", "request"]):
        priority = "low"

    # Auto-determine category
    category = "General IT"
    if any(w in desc_lower for w in ["vpn", "network"]):
        category = "Network - VPN"
    elif any(w in desc_lower for w in ["wifi", "wireless"]):
        category = "Hardware - WiFi"
    elif any(w in desc_lower for w in ["laptop", "screen", "keyboard", "hardware", "battery"]):
        category = "Hardware - Repair"
    elif any(w in desc_lower for w in ["okta", "mfa", "password", "authentication"]):
        category = "Security - Access"
    elif any(w in desc_lower for w in ["slack", "email", "outlook", "software"]):
        category = "Software - Access"

    return {
        "ticket_id": ticket_id,
        "issue_description": issue_description[:200],
        "category": category,
        "priority": priority,
        "status": "open",
        "created_by": created_by,
        "assigned_to": "IT Support Queue",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "estimated_resolution": "24 hours" if priority == "high" else "3-5 business days"
    }
