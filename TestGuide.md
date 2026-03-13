# Complete Testing Guide — Enterprise AI IT Support Assistant

## Prerequisites

1. Make sure all 3 services are running:
   - **MongoDB** (port 27017)
   - **Backend**: `uvicorn server:app --host 0.0.0.0 --port 8001 --reload`
   - **Frontend**: `npm start` (port 3000)
2. Open **http://localhost:3000** in your browser
3. Your `backend/.env` should have a valid `OPENAI_API_KEY`

---

## TEST 1: Login Page

1. You'll see a dark login page
2. In the **Corporate Email** field, type: `john.doe@company.com`
3. Click **Sign In**
4. **Expected:** You're taken to the Chat Dashboard (no password needed — demo login)

---

## TEST 2: Chat Dashboard (Empty State)

After login, verify:
- **Left sidebar** — your name, "+ New Conversation" button, "Evaluation Metrics" and "Feedback Analysis" links
- **Center area** — "Enterprise IT Assistant" with 4 quick-action buttons:
  - Reset Okta MFA
  - VPN Issues
  - WiFi Problems
  - Create Ticket
- **Top right** — green "System Online" indicator
- **Bottom** — text input box

---

## TEST 3: Knowledge Search

1. Click the **"Reset Okta MFA"** quick-action button
2. Wait 5-15 seconds for the AI response
3. **Expected:**
   - A blue **"knowledge search"** badge
   - A green **"high conf."** badge (hover for retrieval score + groundedness %)
   - Step-by-step MFA reset instructions
   - **Sources** section listing documents like "Okta MFA Reset Procedures"
   - Latency indicator (e.g., "8.5s")
   - **Helpful / Not Helpful** buttons below the response

---

## TEST 4: Open a Source Document

1. In the Sources section from Test 3, **click any source** (e.g., "Okta MFA Reset Procedures")
2. **Expected:** A popup dialog opens showing:
   - Document title, category badge, tags
   - Full scrollable document content
3. Click **X** to close

---

## TEST 5: Conditional Query Rewriting

**Test 5a — Vague query (SHOULD rewrite):**
1. Click **"+ New Conversation"**
2. Type: `VPN broken` and press Enter
3. Wait for the AI response
4. **Expected:** A purple **"rewritten"** badge appears above the response
5. Hover over it — tooltip shows the rewritten version (e.g., "How to troubleshoot VPN connection failures...")

**Test 5b — Clear query (should NOT rewrite):**
1. Click **"+ New Conversation"**
2. Type: `How do I reset my Okta MFA using the self-service portal?` and press Enter
3. **Expected:** No purple "rewritten" badge (query was clear enough)

---

## TEST 6: Retrieval Confidence Scoring

**Test 6a — High confidence:**
1. Type: `How do I connect to the company VPN?`
2. **Expected:** Green **"high conf."** badge. Hover shows retrieval score > 0.25

**Test 6b — Low confidence (off-topic):**
1. Click **"+ New Conversation"**
2. Type: `How do I order office furniture?`
3. **Expected:** Red **"low conf."** or yellow **"medium conf."** badge. Response is cautious and may suggest creating a ticket.

---

## TEST 7: Groundedness Evaluation

1. Send any query (e.g., `What is the WiFi password for the office?`)
2. Hover over the confidence badge (green/yellow/red)
3. **Expected tooltip shows two numbers:**
   - **Retrieval score** — how well documents matched (e.g., 0.291)
   - **Groundedness** — percentage (e.g., "Groundedness: 85%")

---

## TEST 8: User Feedback Buttons

1. Below any AI response, find the **Helpful** (thumbs up) and **Not Helpful** (thumbs down) buttons
2. Click **Helpful** on one response
3. **Expected:** Button turns green, shows "Thank you for your feedback"
4. Note: Buttons disable after clicking — can't change
5. On a different response, click **Not Helpful**
6. **Expected:** Button turns red with "Thank you for your feedback"

---

## TEST 9: Troubleshooting with System Check

1. Click **"+ New Conversation"**
2. Type: `My VPN is not connecting` and press Enter
3. **Expected:**
   - Amber **"troubleshooting"** badge
   - Step-by-step troubleshooting instructions
   - A **system check** card showing service status (e.g., "Corporate VPN: operational")
   - Sources with VPN-related documents

---

## TEST 10: Ticket Creation

1. Click **"+ New Conversation"**
2. Type: `Create a ticket for laptop repair` and press Enter
3. **Expected:**
   - Green **"ticket creation"** badge
   - A green **Ticket Created** card showing:
     - Ticket ID (e.g., TKT-1234)
     - Priority: medium
     - Category: Hardware - Repair
     - ETA: 3-5 business days

---

## TEST 11: Safe Fallback — Auto-Escalation

1. Click **"+ New Conversation"**
2. Type: `My VPN is not working and I'm blocked from accessing anything`
3. **Expected:**
   - Troubleshooting steps in the response
   - A green **"Auto-Escalated Ticket"** card at the bottom (auto-created because of urgency keywords + troubleshooting intent)

---

## TEST 12: Safe Fallback — Cautious Response

1. Click **"+ New Conversation"**
2. Type: `How do I set up the office printer?`
3. **Expected:** Response includes a cautious note like: *"I found limited documentation... I recommend creating a support ticket"*
4. No auto-ticket — just a suggestion

---

## TEST 13: New Knowledge Base Documents (Hybrid Search)

Test the 4 new documents added in the expanded knowledge base:

| Query | Expected Top Source |
|---|---|
| `My printer is stuck and not printing` | Printer and Printing Troubleshooting (kb-009) |
| `Teams meeting no sound` | Microsoft Teams Setup and Troubleshooting (kb-010) |
| `OneDrive files not syncing` | OneDrive and SharePoint File Sync (kb-011) |
| `How do I set up Zoom for meetings?` | Zoom Video Conferencing Setup (kb-012) |

For each: verify the correct document appears in the Sources section.

---

## TEST 14: Conversation History

1. Look at the **left sidebar** — all conversations are listed with titles
2. Click any **previous conversation**
3. **Expected:** Full chat history loads with messages, sources, badges, ticket cards, and feedback state

---

## TEST 15: Sidebar Toggle

1. Click the **chat bubble icon** in the top-left header
2. **Expected:** Sidebar hides, full-width chat
3. Click again to bring it back

---

## TEST 16: Evaluation Pipeline

1. In the sidebar, click **"Evaluation Metrics"**
2. Click the blue **"Run Evaluation"** button
3. Wait 30-60 seconds (loading spinner shows)
4. **Expected results:**
   - **4 metric cards**: Retrieval Accuracy, Intent Accuracy, Groundedness Rate, Avg Latency
   - **4 tabs**: Retrieval, Intent, Groundedness, Latency — click each for per-query details
5. Click **"Back to Chat"** to return

---

## TEST 17: Feedback Analysis Dashboard

1. In the sidebar, click **"Feedback Analysis"**
2. **Expected sections:**

| Section | What You See |
|---|---|
| Metric Cards (top) | Total Interactions, Helpful Rate, Not Helpful Rate, Low Confidence %, Ungrounded %, Avg Latency |
| Secondary Stats | Queries Rewritten, Tickets Created, Helpful Responses, No Feedback Yet |
| Failure Breakdown | Failure by Intent + Failure by Category |
| Recommendations | Prioritized suggestions, such as "Increase retrieval top_k" and "Implement hybrid retrieval" |
| Sample Failures | Individual failed queries with confidence, groundedness, feedback, and fix suggestions |

3. Click **"Refresh"** to reload with latest data
4. Click **"Back to Chat"** to return

---

## TEST 18: Additional Queries

Try these and verify the correct intent:

| Query | Expected Intent | Look For |
|------|------|------|
| How do I get access to Slack? | knowledge_search | Slack access guide with sources |
| I forgot my password and I'm locked out | troubleshooting | Password reset steps + system check |
| How do I set up Outlook on my phone? | knowledge_search | Email setup instructions |
| I need to install Visual Studio Code | knowledge_search | Software installation guide |
| Create a ticket for broken keyboard | ticket_creation | Ticket card with Hardware category |

---

## TEST 19: Logout

1. In the sidebar bottom, click on your **name/email** area
2. A dropdown appears — click **"Sign Out"**
3. **Expected:** You're taken back to the login page

---
