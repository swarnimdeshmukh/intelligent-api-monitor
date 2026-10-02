import requests
from app.config import settings
def fallback(i,e):
    src=', '.join(x['source'] for x in e) or 'No runbook matched'
    return f"Summary: {i['title']}. Observed condition: {i['anomaly_reason']}. Severity: {i['severity']}. Evidence: {src}. Recommended response: inspect the endpoint and dependencies, review recent deployments/configuration, apply the relevant runbook remediation, and verify recovery with new samples."
def analyze(i,e):
    c=settings()
    if c.llm_provider.lower()!='ollama' or not c.llm_model:return fallback(i,e)
    ctx='\n\n'.join(f"SOURCE: {x['source']}\n{x['text']}" for x in e)
    try:
        r=requests.post(f"{c.ollama_base_url.rstrip('/')}/api/generate",json={'model':c.llm_model,'prompt':f'Analyze this API incident using only the evidence. Incident: {i}\nRunbooks:\n{ctx}','stream':False},timeout=60); r.raise_for_status(); return r.json().get('response','').strip() or fallback(i,e)
    except requests.RequestException:return fallback(i,e)
