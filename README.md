# CompetitorIQ

### Remember Every Move. Understand the Strategy.

**CompetitorIQ** is an AI-powered competitive intelligence agent that gives competitor analysis a persistent memory.

Instead of treating every question as a completely new conversation, CompetitorIQ remembers historical competitor events, recalls relevant context, connects events across time, detects patterns, and turns that context into evidence-backed strategic intelligence.

The core idea is simple:

> **Don't just analyze what competitors are doing now. Remember what they did before and understand how those events connect.**

---

## What Problem Does It Solve?

Traditional AI assistants are often **stateless**.

Ask:

> "How has Microsoft's AI strategy evolved?"

A stateless system may answer using only the information available to it at that moment.

But competitive intelligence is inherently historical.

A useful analyst needs to remember:

* previous product launches
* pricing changes
* hiring activity
* partnerships
* acquisitions
* technology moves
* messaging changes
* market expansion
* leadership changes

CompetitorIQ uses **Hindsight as the persistent memory layer** so historical context can be retained and recalled when it becomes relevant.

---

## What CompetitorIQ Does

CompetitorIQ provides a complete competitive intelligence workflow:

### 1. AI Analyst

Ask natural-language questions about a competitor.

Examples:

* How has Microsoft's AI strategy evolved?
* What major changes has Google made recently?
* What technology direction is OpenAI taking?
* What patterns exist across a competitor's historical events?

The system retrieves relevant historical context before generating the answer.

---

### 2. Competitor Profiles

Each competitor has a structured profile containing:

* Company name
* Website
* Industry
* Description
* Memory identifier
* Historical events

Competitors have isolated memory so information from one company does not leak into another.

---

### 3. Historical Timeline

CompetitorIQ converts individual events into a chronological timeline.

Events can include:

* Product
* Pricing
* Hiring
* Partnership
* Acquisition
* Messaging
* Funding
* Leadership
* Technology
* Market Expansion

This makes long-term changes easier to understand.

---

### 4. Competitor Comparison

CompetitorIQ can analyze multiple competitors using their separate memory contexts.

For example:

> "How are Microsoft, Google and OpenAI approaching AI?"

The system recalls relevant information for each competitor before generating a comparison.

---

### 5. Memory Explorer

Users can inspect the information stored in the competitor's long-term memory.

This makes the role of Hindsight visible instead of hiding memory behind the interface.

---

### 6. Before vs After Hindsight

One of the core demonstrations of CompetitorIQ is comparing analysis before and after persistent memory.

**Before Hindsight:**

The agent has limited historical context and may produce a shallow analysis.

**After Hindsight:**

The agent recalls relevant historical events and can connect those events to explain how the competitor's strategy has evolved.

This demonstrates the actual behavioral difference created by persistent agent memory.

---

### 7. Connect the Dots

CompetitorIQ looks for relationships between events.

For example:

```text
Product Launch
      ↓
Hiring Activity
      ↓
Technology Investment
      ↓
Messaging Change
      ↓
Strategic Pattern
```

Instead of treating every event independently, the system uses historical memory to identify meaningful connections.

---

### 8. What Changed?

CompetitorIQ tracks new competitor activity against a previous checkpoint.

It can identify:

* new events
* important changes
* historical context
* supporting events
* source information

This creates a foundation for proactive competitive intelligence.

---

### 9. Alerts

Important changes can be converted into alerts containing:

* What changed
* Why it matters
* Event type
* Historical context
* Supporting events
* Confidence
* Source

Alerts are generated from actual stored events rather than fabricated activity.

---

### 10. Executive Intelligence Brief

CompetitorIQ can generate a structured intelligence report containing:

* Executive summary
* Recent activity
* Major patterns
* Strategic signals
* What changed
* Historical context
* Key evidence
* Confidence
* Limitations

The goal is to turn large amounts of historical competitor information into something an analyst or decision-maker can quickly understand.

---

# Architecture

```text
                         COMPETITORIQ
                              │
                              ▼
                    ┌───────────────────┐
                    │   User Question   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Question / Intent │
                    │   Understanding   │
                    └─────────┬─────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌─────────────────┐       ┌─────────────────┐
        │     SQLite      │       │    Hindsight    │
        │ Structured Data │       │ Persistent Memory│
        └────────┬────────┘       └────────┬────────┘
                 │                         │
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    ┌───────────────────┐
                    │   Relevant        │
                    │ Historical Context│
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │       Groq        │
                    │ Reasoning / LLM   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Strategic         │
                    │ Intelligence      │
                    └─────────┬─────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
          Patterns          Alerts         Reports
             │                │                │
             └────────────────┴────────────────┘
                              │
                              ▼
                         Frontend UI
```

---

# Why Hindsight Is Central

Hindsight is not used as an additional feature or decorative component.

It is the **long-term memory layer of CompetitorIQ**.

The core flow is:

```text
Verified Event
      ↓
SQLite
      ↓
Hindsight RETAIN
      ↓
Persistent Competitor Memory
      ↓
Hindsight RECALL
      ↓
Relevant Historical Context
      ↓
Groq Reasoning
      ↓
Intelligence
```

This allows the agent to accumulate knowledge over time instead of starting from zero for every interaction.

---

# Memory Design

Each competitor has its own memory context.

```text
Microsoft
   └── Microsoft Memory

Google
   └── Google Memory

OpenAI
   └── OpenAI Memory

Anthropic
   └── Anthropic Memory

Meta
   └── Meta Memory

Amazon
   └── Amazon Memory
```

This isolation is important because competitor intelligence must remain correctly attributed.

The system also keeps structured event information in SQLite while Hindsight provides the persistent memory required for contextual recall.

---

# Event Ingestion

CompetitorIQ accepts verified competitor events with source information.

Each event contains:

```text
Competitor
Event Type
Title
Description
Event Date
Source Name
Source URL
```

Example:

```json
{
  "competitor": "Microsoft",
  "event_type": "Product",
  "title": "Example verified event",
  "description": "Description of the event",
  "event_date": "YYYY-MM-DD",
  "source_name": "Official Source",
  "source_url": "https://example.com/source"
}
```

Every factual event requires a source.

Duplicate protection prevents the same event from being repeatedly inserted.

---

# Intelligence Flow

When a user asks a question:

```text
User Question
     ↓
Understand Intent
     ↓
Identify Competitor
     ↓
Check Structured Data
     ↓
Recall Relevant Hindsight Memories
     ↓
Filter Relevant Evidence
     ↓
Groq Reasoning
     ↓
Fact / Inference Separation
     ↓
Evidence-backed Answer
```

Hindsight is used when historical or contextual memory is useful.

The system does not blindly force every question through memory.

---

# Example

### Question

> How has Microsoft's AI strategy evolved?

### Without Persistent Memory

The system has limited context and may focus primarily on recent information.

### With Hindsight

The system can recall historical events such as:

```text
Earlier technology activity
        ↓
Product developments
        ↓
Partnership activity
        ↓
Hiring / investment activity
        ↓
Messaging changes
        ↓
Long-term strategic pattern
```

The resulting answer can explain the evolution using evidence from multiple points in time.

---

# Technology Stack

| Layer             | Technology                        |
| ----------------- | --------------------------------- |
| Frontend          | React / existing frontend stack   |
| Backend           | Python + Flask                    |
| Database          | SQLite                            |
| Persistent Memory | Hindsight                         |
| LLM / Reasoning   | Groq                              |
| API Communication | REST                              |
| Memory Operations | Hindsight RETAIN / RECALL         |
| Intelligence      | Pattern detection + LLM reasoning |

---

# Backend Structure

```text
backend/
│
├── app.py
├── config.py
├── requirements.txt
├── .env.example
│
├── routes/
│   ├── competitors.py
│   ├── events.py
│   └── analyst.py
│
├── services/
│   ├── hindsight_service.py
│   ├── llm_service.py
│   ├── database_service.py
│   ├── event_service.py
│   ├── ingestion_service.py
│   ├── pattern_service.py
│   ├── alert_service.py
│   └── report_service.py
│
├── models/
│   └── database.py
│
└── utils/
    └── helpers.py
```

---

# Key API Endpoints

### Health

```http
GET /api/health
```

### Competitors

```http
GET /api/competitors
POST /api/competitors
GET /api/competitors/<id>
GET /api/competitors/<id>/events
GET /api/competitors/<id>/timeline
GET /api/competitors/<id>/patterns
```

### Events

```http
POST /api/events
GET /api/events
GET /api/events/<id>
DELETE /api/events/<id>
```

### Hindsight Memory

```http
POST /api/events/retain
POST /api/memory/recall
```

### Intelligence

```http
POST /api/analyst/analyze
POST /api/analyst/compare
POST /api/analyst/before-after
POST /api/analyst/patterns
```

### Alerts

```http
GET /api/alerts
POST /api/alerts/generate
PATCH /api/alerts/<id>/read
PATCH /api/alerts/<id>/dismiss
```

### Reports

```http
POST /api/reports/competitor
```

---

# Installation

## 1. Clone the repository

```bash
git clone [YOUR_GITHUB_REPOSITORY_URL]
cd CompetitorIQ
```

## 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

## 4. Configure environment variables

Create:

```text
backend/.env
```

Add:

```env
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b

DATABASE_URL=sqlite:///competitoriq.db
```

**Never commit `.env` or API keys to GitHub.**

---

# Running the Backend

From the project directory:

```bash
python backend/app.py
```

The backend exposes the REST API used by the frontend.

Check:

```http
GET /api/health
```

---

# Hindsight Integration

CompetitorIQ uses two important Hindsight operations:

### RETAIN

Events are stored as persistent competitor memory.

```text
Verified Event
      ↓
Hindsight RETAIN
      ↓
Competitor Memory
```

### RECALL

When intelligence is requested, relevant historical context is retrieved.

```text
User Question
      ↓
Hindsight RECALL
      ↓
Relevant Memories
      ↓
Groq
      ↓
Answer
```

This separation allows SQLite to handle structured application data while Hindsight handles long-term contextual memory.

---

# Evidence & Reliability

CompetitorIQ is designed around evidence-backed intelligence.

The system:

* requires sources for factual events
* preserves event dates
* keeps source URLs
* separates facts from inference
* avoids unsupported causation
* avoids fabricated historical events
* reports limitations when memory is insufficient
* maintains separate competitor memory
* avoids presenting unsupported predictions as facts

---

# Before vs After

The central behavioral difference is:

```text
WITHOUT MEMORY

Question
   ↓
Limited Context
   ↓
Generic / Recent Analysis


WITH HINDSIGHT

Question
   ↓
Historical Recall
   ↓
Relevant Events
   ↓
Connected Patterns
   ↓
Evidence-backed Intelligence
```

The purpose of the project is not simply to add memory to an agent.

It is to make historical memory useful for reasoning.

---

# Screenshots

Add project screenshots here before publishing the repository.

Recommended screenshots:

1. CompetitorIQ dashboard
2. AI Analyst
3. Competitor timeline
4. Memory Explorer
5. Before vs After Hindsight
6. Connect the Dots
7. What Changed / Alerts
8. Executive Intelligence Brief

Example:

```markdown
![CompetitorIQ Dashboard](docs/images/dashboard.png)
```

---

# Demo

### Live Demo

[ADD LIVE DEMO URL]


### Project Article
(https://www.linkedin.com/pulse/competitor-iq-srinivasula-b-v-l-n-akhil-c1nvc)

---

# Documentation & Resources

### Hindsight

[Hindsight GitHub Repository](https://github.com/vectorize-io/hindsight?utm_source=chatgpt.com)

[Hindsight Documentation](https://hindsight.vectorize.io/?utm_source=chatgpt.com)

### Agent Memory

[What is Agent Memory — Vectorize](https://vectorize.io/what-is-agent-memory?utm_source=chatgpt.com)

---

# Project Links

| Resource               | Link                                                                         |
| ---------------------- | -----------------------------------------                                    |                      |
| Technical Article      | https://www.linkedin.com/pulse/competitor-iq-srinivasula-b-v-l-n-akhil-c1nvc |
| Hindsight GitHub       | https://github.com/vectorize-io/hindsight                                    |
| Hindsight Docs         | https://hindsight.vectorize.io/                                              |
| Vectorize Agent Memory | https://vectorize.io/what-is-agent-memory                                    |

---

# Key Takeaways

### 1. Memory should change behavior

Persistent memory is useful when it allows an agent to use information from previous interactions and events.

### 2. Structured data and memory solve different problems

SQLite handles structured competitor and event data.

Hindsight handles persistent contextual memory.

### 3. Recall should happen before reasoning

The system retrieves relevant historical context before asking the LLM to generate intelligence.

### 4. Evidence matters

Every factual event is associated with source information so the resulting intelligence can be traced back to evidence.

### 5. Memory enables longitudinal analysis

Instead of asking only:

> "What happened?"

CompetitorIQ can ask:

> "What happened before, what changed, and how are these events connected?"

---

# Future Improvements

Potential extensions include:

* automated verified-source ingestion
* broader source connectors
* richer event extraction
* improved relevance ranking for recalled memories
* deeper temporal pattern analysis
* additional competitor intelligence dimensions
* analyst feedback loops
* larger-scale deployment

---

# Built With

**Hindsight** — persistent agent memory
**Groq** — LLM reasoning
**SQLite** — structured competitor/event data
**Python + Flask** — backend orchestration
**React** — frontend interface

---

## Author

Built by **Akhil** and the CompetitorIQ team.

> Remember every move. Understand the strategy.
