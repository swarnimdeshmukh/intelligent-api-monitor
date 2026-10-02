from fastapi import FastAPI
from app.db import init_db
from app.monitoring.store import recent
from app.incidents.manager import recent as incidents
app=FastAPI(title='Intelligent API Monitoring API')
@app.on_event('startup')
def startup():init_db()
@app.get('/health')
def health():return {'status':'ok'}
@app.get('/metrics')
def metrics(limit:int=100):return recent(limit)
@app.get('/incidents')
def get_incidents(limit:int=50):return incidents(limit)
