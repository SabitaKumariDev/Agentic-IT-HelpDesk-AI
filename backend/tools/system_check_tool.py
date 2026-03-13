"""
System Check Tool
Simulates checking the health and status of enterprise IT services.
"""

import random


def simulate_system_check(service):
    """Simulate checking the status of an IT service."""
    services = {
        "vpn": {
            "name": "Corporate VPN (GlobalProtect)",
            "status": random.choice(["operational", "degraded", "operational", "operational"]),
            "latency": f"{random.randint(20, 150)}ms",
            "active_connections": random.randint(1200, 5000),
            "details": "All VPN gateways are operational. Minor latency on US-East gateway."
        },
        "wifi": {
            "name": "Corporate WiFi Network",
            "status": random.choice(["operational", "operational", "degraded"]),
            "access_points": random.randint(150, 300),
            "connected_devices": random.randint(800, 2000),
            "details": "WiFi infrastructure healthy. All access points responding."
        },
        "email": {
            "name": "Microsoft 365 / Outlook",
            "status": "operational",
            "mail_flow": "normal",
            "queue_length": random.randint(0, 50),
            "details": "Email services running normally. No delivery delays detected."
        },
        "slack": {
            "name": "Slack Enterprise",
            "status": "operational",
            "api_status": "healthy",
            "workspace_status": "active",
            "details": "Slack services fully operational."
        },
        "okta": {
            "name": "Okta Identity Platform",
            "status": "operational",
            "auth_success_rate": f"{random.uniform(99.0, 99.9):.1f}%",
            "mfa_status": "active",
            "details": "Okta SSO and MFA services operational."
        },
        "general": {
            "name": "General IT Infrastructure",
            "status": "operational",
            "services_up": f"{random.randint(45, 50)}/50",
            "details": "Most enterprise services are operational."
        }
    }

    return services.get(service, services["general"])
