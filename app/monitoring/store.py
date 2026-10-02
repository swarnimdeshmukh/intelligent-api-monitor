from app.db import connection
def save(m,score,reason,anomaly):
    with connection() as db:
        db.execute('INSERT INTO metrics(timestamp,target,latency_ms,status_code,success,error_rate,throughput,anomaly_score,anomaly_reason,is_anomaly) VALUES(?,?,?,?,?,?,?,?,?,?)',(m.timestamp,m.target,m.latency_ms,m.status_code,int(m.success),m.error_rate,m.throughput,score,reason,int(anomaly))); db.commit()
def recent(limit=500):
    with connection() as db: rows=db.execute('SELECT * FROM metrics ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
    return [dict(x) for x in rows]
