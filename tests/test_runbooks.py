from pathlib import Path
def test_runbooks(): assert len(list(Path('data/runbooks').glob('*.md')))>=4


def test_rag_retrieval():
    from app.rag.retriever import retrieve

    results = retrieve("HTTP 500 server error", 3)

    assert len(results) > 0
    assert results[0]["source"] == "http_errors.md"


def test_incident_deduplication():
    from app.db import init_db
    from app.monitoring.collector import collect
    from app.incidents.manager import create

    init_db()

    metric = collect(
        "http://127.0.0.1:8000/error",
        5,
    )

    first = create(
        metric,
        -1.0,
        "HTTP 500 server error",
    )

    second = create(
        metric,
        -1.0,
        "HTTP 500 server error",
    )

    assert first == second
