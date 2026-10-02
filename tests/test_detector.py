from types import SimpleNamespace
from app.anomaly.detector import HybridDetector
def test_http_500():
    m=SimpleNamespace(latency_ms=10,status_code=500,error_rate=1,throughput=1); assert HybridDetector().detect(m)[1]
def test_slow():
    m=SimpleNamespace(latency_ms=3500,status_code=200,error_rate=0,throughput=.2); assert HybridDetector().detect(m)[1]
