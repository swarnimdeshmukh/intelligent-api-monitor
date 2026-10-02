# Intelligent API Monitoring & Incident Response System

Complete local-first API observability project.

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Terminal 1:
```bash
source .venv/bin/activate
uvicorn app.test_service:app --host 127.0.0.1 --port 8000
```

Terminal 2:
```bash
source .venv/bin/activate
python -m app.monitoring.service
```

Terminal 3:
```bash
source .venv/bin/activate
streamlit run dashboard/dashboard.py
```

Tests:
```bash
pytest -q
```

Endpoints: `/health`, `/users`, `/products`, `/slow`, `/error`.

The detector combines deterministic operational rules with Isolation Forest. Runbook retrieval uses Sentence Transformers + FAISS. Incident analysis works locally without a cloud API and can optionally use Ollama.
