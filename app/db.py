import sqlite3
from pathlib import Path
from app.config import settings
def connection():
    p=Path(settings().database_path); p.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(p); c.row_factory=sqlite3.Row; return c
def init_db():
    with connection() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS metrics(id INTEGER PRIMARY KEY AUTOINCREMENT,timestamp TEXT,target TEXT,latency_ms REAL,status_code INTEGER,success INTEGER,error_rate REAL,throughput REAL,anomaly_score REAL,anomaly_reason TEXT,is_anomaly INTEGER)''')
        db.execute('''CREATE TABLE IF NOT EXISTS incidents(id INTEGER PRIMARY KEY AUTOINCREMENT,incident_id TEXT UNIQUE,timestamp TEXT,target TEXT,severity TEXT,status TEXT,title TEXT,details TEXT,anomaly_score REAL,anomaly_reason TEXT,analysis TEXT,evidence TEXT)''')
        db.commit()
