---
name: vertex-monitor
description: >-
  Query Vertex AI budget balance, spending status, and available models
  through VertexMonitor proxy. Activates when users ask about their
  Vertex AI budget, remaining balance, spending details, or available
  models. Triggers on phrases like: query vertex balance, check vertex
  budget, how much vertex credit left, vertex usage, vertex available
  models, 查询 Vertex 余额, 查询 Vertex 用量, Vertex 还剩多少额度.
license: MIT
compatibility: >-
  Works with any AI Agent supporting the Agent Skills Open Standard
  (SKILL.md): Claude Code, GitHub Copilot, Cursor, Windsurf, Cline,
  OpenAI Codex CLI, Gemini CLI, Hermes Agent, and 20+ others.
  Requires VertexMonitor proxy running at http://localhost:8899.
metadata:
  mda:
    title: VertexMonitor Agent Skill
    version: "1.0.0"
    tags: [vertex-ai, budget, monitoring, proxy]
    requires:
      network: ["localhost:8899"]
---

# /vertex-monitor — Vertex AI Budget & Model Query

Query Vertex AI budget balance, spending status, and available models
through the VertexMonitor proxy service.

## Trigger

This skill activates when the user asks about:
- Vertex AI budget or balance
- How much credit or spending remains
- Vertex usage or spending details
- Available Vertex AI models

Example triggers:
- "查询 Vertex 余额" / "Query Vertex balance"
- "Vertex 还剩多少额度？" / "How much Vertex credit left?"
- "查询 Vertex 用量" / "Check Vertex usage"
- "查询 Vertex 可用模型" / "What Vertex models are available?"

## Instructions

When this skill is invoked, determine which tool to call based on
the user's request.

### query_balance — Query Budget Balance & Spending

Call when the user asks about budget, balance, remaining credit,
or spending status.

**Endpoint:** `GET http://localhost:8899/skill/balance`

**Response fields:**
- `status` — Budget status: `healthy`, `warning`, or `exhausted`
- `balance` — Total budget amount
- `spent` — Amount spent this period
- `remaining` — Remaining budget
- `expires_at` — Budget expiry date
- `mode` — Billing mode (`manual` or `auto_recurring`)
- `message` — Human-readable status summary

Example response:
```json
{
  "status": "healthy",
  "balance": 118.50,
  "spent": 0.048293,
  "remaining": 118.451707,
  "expires_at": "2027-05-23T23:59:59",
  "mode": "manual",
  "message": "🟢 Budget status: healthy. Remaining $118.45 of $118.50 (spent $0.05)."
}
```

After receiving the response, present the information in a clear,
human-readable format. Highlight the status and remaining budget.

### query_models — Query Available Models

Call when the user asks about available models or which model to use.

**Endpoint:** `GET http://localhost:8899/skill/models`

**Response fields:**
- `models` — List of allowed model identifiers
- `default_model` — The default model
- `count` — Number of available models

Example response:
```json
{
  "models": ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.1-pro-preview"],
  "default_model": "gemini-3.1-flash-lite",
  "count": 3
}
```

Present the model list and mention the default model.

## Examples

### Example 1: Query Balance

User: "查询 Vertex 余额"

Agent calls `GET http://localhost:8899/skill/balance`

Agent responds: "Your Vertex AI budget is healthy. Remaining $118.45
of $118.50 (spent $0.05). Expires 2027-05-23."

### Example 2: Query Available Models

User: "查询 Vertex 可用模型"

Agent calls `GET http://localhost:8899/skill/models`

Agent responds: "3 Vertex AI models available:
gemini-3.1-flash-lite (default), gemini-3.5-flash,
gemini-3.1-pro-preview."

### Example 3: Budget Status Check

User: "Vertex 还剩多少额度？"

Agent calls `GET http://localhost:8899/skill/balance`

Agent responds: "Vertex AI budget is healthy. Remaining $118.45
of $118.50. You've spent $0.05 so far this period."
