# CompetitorIQ Backend & Real Hindsight Integration

CompetitorIQ is an autonomous Competitive Intelligence Agent powered by **Hindsight** episodic memory and **Groq** strategic reasoning.

---

## 1. Hindsight Architecture

CompetitorIQ uses the official `hindsight-client` Python SDK to create isolated memory banks for each tracked competitor:

```
Competitor Event Ingestion
           ↓
   Flask API Gateway
           ↓
  HindsightService (services/hindsight_service.py)
           ↓
  Hindsight Cloud (https://api.hindsight.vectorize.io)
  ├── Bank: 'competitor-nova-ai'   (NovaAI memory bank)
  ├── Bank: 'competitor-cloud-mind' (CloudMind memory bank)
  └── Bank: 'competitor-tech-flow'  (TechFlow memory bank)
```

---

## 2. Quickstart & Running Locally

### Prerequisites
- Python 3.10+
- Installed dependencies: `pip install -r requirements.txt`

### Start Backend Server
```bash
cd backend
python app.py
```
Server runs at `http://127.0.0.1:5000` (or `http://localhost:5000`).

### Run Hindsight Integration Tests
```bash
cd backend
python test_hindsight.py
```
This runs the 4 integration tests against the live Hindsight memory platform.

---

## 3. Endpoints

### Retain Competitor Event
`POST /api/events/retain`
```json
{
  "competitor": "NovaAI",
  "event_type": "Pricing Change",
  "event_date": "2026-03-15",
  "title": "NovaAI reduces enterprise pricing by 15%",
  "description": "NovaAI announced a 15% reduction in enterprise contract pricing.",
  "source": "Official Press Release"
}
```

### Recall Competitor Historical Memory
`POST /api/memory/recall`
```json
{
  "competitor": "NovaAI",
  "query": "How has NovaAI pricing strategy changed over time?",
  "top_k": 5
}
```

### Health Check
`GET /api/health`
Reports SQLite status and Hindsight memory engine readiness.

---

## 4. AI Analyst Reasoning (Groq + Hindsight)

### Analyze Strategic Trajectory
`POST /api/analyst/analyze`
```json
{
  "competitor": "NovaAI",
  "question": "How has NovaAI's pricing strategy changed over time?"
}
```

**Architecture & Flow:**
```
User Question
    ↓
Identify Competitor
    ↓
Hindsight RECALL (Bank: 'competitor-nova-ai')
    ↓
Retrieve Relevant Historical Memories
    ↓
Groq LLM Reasoning (openai/gpt-oss-120b)
    ↓
Connect Events Across Time & Synthesize Trajectory
    ↓
Return Structured Intelligence + Evidence + Memory Transparency
```

**Response Format:**
```json
{
  "status": "success",
  "competitor": "NovaAI",
  "question": "How has NovaAI's pricing strategy changed over time?",
  "answer": "...",
  "pattern": "Upmarket Enterprise Pivot",
  "strategic_signal": "Abandoning developer freemium to pursue six-figure ACV contracts",
  "why_it_matters": "Increases competitive pressure on enterprise deals while ceding SMB developer segment",
  "key_events": [...],
  "confidence": "High (Evidence Supported)",
  "memory_used": true,
  "memory_count": 10,
  "relevant_date_range": {
    "start": "2024-06-15",
    "end": "2026-09-28"
  },
  "evidence": [...]
}
```

### Analyst Test Suite
```bash
cd backend
python test_analyst.py
```
