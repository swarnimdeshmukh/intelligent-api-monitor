import pandas as pd,plotly.express as px,streamlit as st
from app.db import init_db
from app.monitoring.store import recent
from app.incidents.manager import recent as incidents
st.set_page_config(page_title='Intelligent API Monitoring',page_icon='⚡',layout='wide'); init_db()
st.title('⚡ Intelligent API Monitoring & Incident Response'); st.caption('Monitoring • Hybrid anomaly detection • Incidents • RAG • AI-assisted analysis')
m=pd.DataFrame(recent(1000)); i=pd.DataFrame(incidents(200))
a,b,c,d=st.columns(4); a.metric('Metrics',len(m)); b.metric('Open Incidents',int((i.status=='OPEN').sum()) if not i.empty else 0); c.metric('Anomalies',int(m.is_anomaly.sum()) if not m.empty else 0); d.metric('Targets',int(m.target.nunique()) if not m.empty else 0)
if not m.empty:
    m['timestamp']=pd.to_datetime(m.timestamp); st.subheader('Latency by Target'); st.plotly_chart(px.line(m.sort_values('timestamp'),x='timestamp',y='latency_ms',color='target',markers=True),use_container_width=True); st.subheader('Recent Metrics'); st.dataframe(m.sort_values('timestamp',ascending=False).head(100),use_container_width=True,hide_index=True)
else:st.info('Waiting for monitoring data...')
st.subheader('Incidents')
if i.empty:st.success('No incidents recorded yet.')
else:
    for _,r in i.iterrows():
        with st.expander(f"{r['severity']} | {r['incident_id']} | {r['target']}"):
            st.write(f"**Reason:** {r['anomaly_reason']}"); st.write(f"**Details:** {r['details']}"); st.write('**Incident Analysis**'); st.write(r['analysis'] or 'Pending'); st.write('**RAG Evidence**'); st.code(r['evidence'] or 'None')
