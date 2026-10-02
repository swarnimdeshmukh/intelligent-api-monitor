from app.monitoring.collector import collect
def test_shape():
    m=collect('http://127.0.0.1:8000/health',5); assert m.latency_ms>=0
