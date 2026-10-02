import time
from app.config import settings
from app.db import init_db
from app.monitoring.collector import collect
from app.monitoring.store import save
from app.anomaly.detector import HybridDetector
from app.incidents.manager import create,update,recent
from app.rag.retriever import retrieve
from app.analyst.analyzer import analyze
def cycle(detector):
    c=settings(); n=0
    for target in c.targets:
        m=collect(target,c.request_timeout_seconds); score,flag,reason=detector.detect(m); save(m,score,reason,flag)
        if flag:
            iid=create(m,score,reason); evidence=retrieve(f'{target} {reason} latency HTTP error database service',c.rag_top_k); i=recent(1)[0]; update(iid,analyze(i,evidence),'\n'.join(f"{x['source']} | similarity={x['score']:.3f}" for x in evidence)); n+=1
    return n
def main():
    init_db(); d=HybridDetector(); print('=== Intelligent API Monitoring Service ==='); print('Monitoring started.')
    while True:
        try:
            n=cycle(d)
            if n:print(f'Created {n} incident(s).')
            time.sleep(settings().monitor_interval_seconds)
        except KeyboardInterrupt: print('\nMonitoring stopped.'); break
if __name__=='__main__':main()
