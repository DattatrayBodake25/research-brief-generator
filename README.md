# 🧠 Research Brief Generator

An **AI-powered research assistant** that generates structured, context-aware research briefs with support for:
- REST API (FastAPI + Swagger UI)
- CLI commands for local usage
- Background job processing
- Context-aware follow-up queries
- Deployment-ready (Docker + Render)

---

## 🚀 Live Demo

- **API Base URL** → [https://research-brief-generator-7mtw.onrender.com](https://research-brief-generator-7mtw.onrender.com)  
- **Swagger Docs** → [https://research-brief-generator-7mtw.onrender.com/docs](https://research-brief-generator-7mtw.onrender.com/docs)  
- **Postman Testing Example** →  
  - `POST https://research-brief-generator-7mtw.onrender.com/brief`  
  - `GET https://research-brief-generator-7mtw.onrender.com/brief/{brief_id}`  

---

## ✨ Features

- Generate structured **research briefs** (executive summary, key findings, analysis, recommendations, references).
- **Asynchronous background processing** for long-running tasks.
- REST API with **Swagger UI** (`/docs`) for easy exploration.
- CLI for **quick local testing**.
- **Context awareness** → supports follow-up queries.
- Production-ready setup: Docker, Render, CI-ready tests.

---

## 📂 Project Structure
```bash
research-brief-generator/
├── src/
│ ├── main.py # Entry point
│ ├── api/
│ │ ├── server.py # FastAPI app & routes
│ │ └── routes.py # API endpoints
│ ├── core/
│ │ ├── graph.py # LangGraph orchestration
│ │ ├── state.py # Research state machine
│ │ ├── nodes.py # Nodes (fetch, summarize, analyze)
│ │ └── tools.py # Tool integrations (web search, etc.)
│ ├── models/
│ │ ├── schemas.py # Pydantic schemas
│ │ └── storage.py # Storage for briefs
│ ├── utils/
│ │ ├── config.py # Settings (env, API keys)
│ │ └── logger.py # Logger setup
│ └── cli/
│ └── main.py # CLI entrypoint
├── requirements.txt # Python deps
├── Makefile # Common tasks
└── README.md # Project docs
```

---

## ⚙️ Installation & Setup

### 1. Clone the repo
```bash
git clone https://github.com/DattatrayBodake25/research-brief-generator.git
cd research-brief-generator
```

## Create virtual environment & install deps
```bash
python -m venv venv
```
```bash
source venv/bin/activate   # On Windows: venv\Scripts\activate
```
```bash
pip install -r requirements.txt
```

## Copy environment variables
```bash
cp .env.example .env
```
Update .env with API keys (OpenAI, Tavily, etc.).

## Running Locally
1. Run API server
```bash
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
```
Now visit:
Swagger UI → http://localhost:8000/docs
Health Check → http://localhost:8000/health

2. Run CLI
```bash
python -m src.cli.main generate-brief "AI in Healthcare" --depth 2 --user test-user
```

Example output:
```bash
✓ Research brief generated successfully!

Topic: AI in Healthcare
Brief ID: AIH-2-2023-04-27
Executive Summary: ...
Key Findings: ...
Recommendations: ...
References: ...
```

## API Usage (Postman / cURL)
1. Create a brief
```bash
POST https://research-brief-generator-7mtw.onrender.com/brief
Content-Type: application/json

{
  "topic": "AI in Education",
  "depth": 2,
  "follow_up": true,
  "user_id": "12345"
}


Response:

{
  "brief_id": "82a16f0b-cb17-42c3-8bd0-617c6c4d8cb4",
  "topic": "AI in Education",
  "status": "processing",
  "message": "Research started in background"
}
```
2. Retrieve a brief
```bash
GET https://research-brief-generator-7mtw.onrender.com/brief/{brief_id}


Response (completed brief):

{
  "status": "completed",
  "request": { ... },
  "result": {
    "executive_summary": "...",
    "key_findings": [...],
    "recommendations": [...]
  }
}

```

## Deployment
Render (live link)
App deployed at → https://research-brief-generator-7mtw.onrender.com







