from collections import defaultdict
import numpy as np
from sklearn.ensemble import IsolationForest
class HybridDetector:
    def __init__(self): self.history=defaultdict(list); self.models={}
    def features(self,m): return [m.latency_ms,m.error_rate,m.throughput,float(m.status_code or 0)]
    def detect(self,m):
        if m.status_code is not None and m.status_code>=500: return -1.0,True,f'HTTP {m.status_code} server error'
        if m.status_code is None: return -1.0,True,'Target unreachable or request timed out'
        if m.latency_ms>=3000: return -.8,True,f'Critical latency: {m.latency_ms:.0f} ms'
        if m.latency_ms>=1000: return -.5,True,f'High latency: {m.latency_ms:.0f} ms'
        h=self.history[m.target]; h.append(self.features(m))
        if len(h)<12: return 0.0,False,'Collecting baseline'
        model=self.models.setdefault(m.target,IsolationForest(n_estimators=150,contamination=.12,random_state=42))
        x=np.asarray(h[-200:],float); model.fit(x); cur=np.asarray([self.features(m)])
        score=float(model.decision_function(cur)[0]); abnormal=int(model.predict(cur)[0])==-1
        return score,abnormal,'Isolation Forest anomaly' if abnormal else 'Normal'
