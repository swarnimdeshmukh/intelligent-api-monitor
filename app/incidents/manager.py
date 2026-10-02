from datetime import datetime,timezone
from uuid import uuid4
from app.db import connection
def severity(m):
    if m.status_code is None or (m.status_code and m.status_code>=500): return 'CRITICAL'
    if m.latency_ms>=3000:return 'HIGH'
    if m.latency_ms>=1000:return 'MEDIUM'
    return 'LOW'
def create(m,score,reason):
    iid='INC-'+uuid4().hex[:8].upper(); sev=severity(m); title=f'{sev}: anomaly detected on {m.target}'
    details=f'Latency={m.latency_ms:.2f} ms | HTTP={m.status_code} | Error rate={m.error_rate:.2f} | Throughput={m.throughput:.2f} req/s'
    with connection() as db:
        db.execute('INSERT INTO incidents(incident_id,timestamp,target,severity,status,title,details,anomaly_score,anomaly_reason,analysis,evidence) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(iid,datetime.now(timezone.utc).isoformat(),m.target,sev,'OPEN',title,details,score,reason,'','')); db.commit()
    return iid
def recent(limit=50):
    with connection() as db: rows=db.execute('SELECT * FROM incidents ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
    return [dict(x) for x in rows]
def update(iid,analysis,evidence):
    with connection() as db: db.execute('UPDATE incidents SET analysis=?,evidence=? WHERE incident_id=?',(analysis,evidence,iid)); db.commit()
