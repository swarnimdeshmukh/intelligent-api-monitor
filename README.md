# Intelligent API Monitoring & Incident Response System

Complete local-first API observability project.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Terminal 1 — API Test Service

```bash
source .venv/bin/activate
uvicorn app.test_service:app --host 127.0.0.1 --port 8000
```

### Terminal 2 — Monitoring Service

```bash
source .venv/bin/activate
python -m app.monitoring.service
```

### Terminal 3 — Streamlit Dashboard

```bash
source .venv/bin/activate
PYTHONPATH=. streamlit run dashboard/dashboard.py
```

## Tests

```bash
pytest -q
```

## Endpoints

- `/health`
- `/users`
- `/products`
- `/slow`
- `/error`

## System Overview

The detector combines deterministic operational rules with Isolation Forest for anomaly detection.

Runbook retrieval uses Sentence Transformers with FAISS for local semantic search.

Incident analysis works locally without requiring a cloud API and can optionally use Ollama for local LLM-based analysis.

## Main Components

- **FastAPI** — API test service
- **Monitoring Service** — collects API metrics
- **Hybrid Anomaly Detector** — deterministic rules + Isolation Forest
- **Incident Manager** — creates and deduplicates active incidents
- **RAG Runbook Retrieval** — Sentence Transformers + FAISS
- **Incident Analyst** — local fallback analysis with optional Ollama
- **SQLite** — local metric and incident storage
- **Streamlit** — monitoring dashboard
- **Pytest** — automated testing

## Project Structure

```text
intelligent-api-monitor-v2/
├── app/
│   ├── analyst/
│   ├── anomaly/
│   ├── incidents/
│   ├── monitoring/
│   ├── rag/
│   ├── api.py
│   ├── config.py
│   ├── db.py
│   └── test_service.py
├── dashboard/
│   └── dashboard.py
├── data/
│   ├── runbooks/
│   │   ├── api_latency.md
│   │   ├── database.md
│   │   ├── http_errors.md
│   │   └── service_degradation.md
│   └── .gitkeep
├── models/
│   └── .gitkeep
├── tests/
│   ├── test_api.py
│   ├── test_collector.py
│   ├── test_detector.py
│   └── test_runbooks.py
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## Local-First Design

The project is designed to run locally.

- API monitoring runs locally.
- Metrics and incidents are stored in SQLite.
- Runbook retrieval uses local embeddings and FAISS.
- Incident analysis has a local fallback.
- Ollama can optionally be used for local LLM-based analysis.

No cloud API is required for the core monitoring, anomaly detection, incident management, or runbook retrieval workflow.