from fastapi.testclient import TestClient
from app.test_service import app
c=TestClient(app)
def test_health(): assert c.get('/health').status_code==200
def test_error(): assert c.get('/error').status_code==500
