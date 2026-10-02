from dataclasses import dataclass
from datetime import datetime,timezone
import time,requests
@dataclass
class Metric:
    timestamp:str; target:str; latency_ms:float; status_code:int|None; success:bool; error_rate:float; throughput:float
def collect(target,timeout):
    t=time.perf_counter(); status=None; ok=False
    try:
        r=requests.get(target,timeout=timeout); status=r.status_code; ok=200<=status<400
    except requests.RequestException: pass
    ms=(time.perf_counter()-t)*1000
    return Metric(datetime.now(timezone.utc).isoformat(),target,round(ms,2),status,ok,0.0 if ok else 1.0,round(1000/max(ms,1),2))
