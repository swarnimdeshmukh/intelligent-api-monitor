cat > dashboard/dashboard.py <<'PY'
import pandas as pd
import plotly.express as px
import streamlit as st

from app.db import init_db
from app.monitoring.store import recent
from app.incidents.manager import recent as incidents


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Intelligent API Monitoring",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("⚡ Intelligent API Monitoring")
st.caption(
    "Real-time API health • Hybrid anomaly detection • "
    "Incident response • RAG runbooks • AI-assisted analysis"
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:
    st.header("Monitoring Console")

    refresh = st.button("🔄 Refresh Data", use_container_width=True)

    st.divider()

    st.markdown(
        """
        **System Components**

        🟢 API Monitoring  
        🟢 Anomaly Detection  
        🟢 Incident Management  
        🟢 RAG Runbooks  
        🟢 AI Analysis
        """
    )

    st.divider()

    st.caption("Intelligent API Monitoring System")


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

metrics_raw = recent(1000)
incidents_raw = incidents(200)

metrics = pd.DataFrame(metrics_raw)
incident_df = pd.DataFrame(incidents_raw)


# ---------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------

metric_count = len(metrics)

open_incidents = (
    int((incident_df["status"] == "OPEN").sum())
    if not incident_df.empty and "status" in incident_df.columns
    else 0
)

anomaly_count = (
    int(metrics["is_anomaly"].sum())
    if not metrics.empty and "is_anomaly" in metrics.columns
    else 0
)

target_count = (
    int(metrics["target"].nunique())
    if not metrics.empty and "target" in metrics.columns
    else 0
)


# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "📊 Metrics Collected",
    metric_count,
)

c2.metric(
    "🚨 Open Incidents",
    open_incidents,
)

c3.metric(
    "⚠️ Anomalies",
    anomaly_count,
)

c4.metric(
    "🎯 Monitored Targets",
    target_count,
)


st.divider()


# ---------------------------------------------------------
# Endpoint health
# ---------------------------------------------------------

st.subheader("🎯 Endpoint Health")

if metrics.empty:
    st.info("Waiting for monitoring data...")
else:
    latest = (
        metrics.sort_values("timestamp")
        .groupby("target")
        .tail(1)
        .copy()
    )

    health_rows = []

    for _, row in latest.iterrows():
        status = row.get("status_code")

        if status is None or pd.isna(status):
            health = "🔴 Unreachable"
        elif int(status) >= 500:
            health = "🔴 Critical"
        elif float(row.get("latency_ms", 0)) >= 1000:
            health = "🟠 Degraded"
        else:
            health = "🟢 Healthy"

        health_rows.append(
            {
                "Endpoint": row["target"],
                "Health": health,
                "Latency (ms)": round(float(row["latency_ms"]), 2),
                "Status": int(status) if not pd.isna(status) else "N/A",
                "Error Rate": round(float(row["error_rate"]) * 100, 2),
            }
        )

    health_df = pd.DataFrame(health_rows)

    st.dataframe(
        health_df,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Charts
# ---------------------------------------------------------

if not metrics.empty:

    metrics["timestamp"] = pd.to_datetime(metrics["timestamp"])

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("⏱️ Latency")

        latency_fig = px.line(
            metrics.sort_values("timestamp"),
            x="timestamp",
            y="latency_ms",
            color="target",
            markers=True,
            labels={
                "latency_ms": "Latency (ms)",
                "timestamp": "Time",
                "target": "Endpoint",
            },
        )

        latency_fig.update_layout(
            legend_title_text="Endpoint",
            hovermode="x unified",
        )

        st.plotly_chart(
            latency_fig,
            use_container_width=True,
        )

    with chart_col2:
        st.subheader("📉 Error Rate")

        error_fig = px.line(
            metrics.sort_values("timestamp"),
            x="timestamp",
            y="error_rate",
            color="target",
            markers=True,
            labels={
                "error_rate": "Error Rate",
                "timestamp": "Time",
                "target": "Endpoint",
            },
        )

        error_fig.update_layout(
            legend_title_text="Endpoint",
            hovermode="x unified",
        )

        st.plotly_chart(
            error_fig,
            use_container_width=True,
        )


# ---------------------------------------------------------
# Distribution charts
# ---------------------------------------------------------

if not metrics.empty:

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.subheader("📡 HTTP Status Distribution")

        status_data = (
            metrics["status_code"]
            .fillna(0)
            .astype(int)
            .astype(str)
            .value_counts()
            .reset_index()
        )

        status_data.columns = ["Status Code", "Count"]

        status_fig = px.bar(
            status_data,
            x="Status Code",
            y="Count",
            text="Count",
        )

        st.plotly_chart(
            status_fig,
            use_container_width=True,
        )

    with chart_col4:
        st.subheader("🚨 Incident Severity")

        if not incident_df.empty:

            severity_data = (
                incident_df["severity"]
                .value_counts()
                .reset_index()
            )

            severity_data.columns = ["Severity", "Count"]

            severity_fig = px.bar(
                severity_data,
                x="Severity",
                y="Count",
                color="Severity",
                text="Count",
            )

            st.plotly_chart(
                severity_fig,
                use_container_width=True,
            )

        else:
            st.info("No incidents recorded yet.")


# ---------------------------------------------------------
# Recent metrics
# ---------------------------------------------------------

st.subheader("📋 Recent Metrics")

if metrics.empty:
    st.info("No metrics available.")
else:

    display_columns = [
        column
        for column in [
            "timestamp",
            "target",
            "latency_ms",
            "status_code",
            "success",
            "error_rate",
            "throughput",
            "is_anomaly",
        ]
        if column in metrics.columns
    ]

    recent_metrics = (
        metrics.sort_values(
            "timestamp",
            ascending=False,
        )
        .head(100)
    )

    st.dataframe(
        recent_metrics[display_columns],
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Incident Response
# ---------------------------------------------------------

st.divider()

st.subheader("🚨 Incident Response")

if incident_df.empty:

    st.success("No incidents recorded yet.")

else:

    for _, incident in incident_df.iterrows():

        severity_value = incident.get("severity", "UNKNOWN")
        incident_id = incident.get("incident_id", "N/A")
        target = incident.get("target", "Unknown")

        with st.expander(
            f"{severity_value} | {incident_id} | {target}"
        ):

            left, right = st.columns(2)

            with left:

                st.markdown("### Incident Details")

                st.write(
                    f"**Status:** {incident.get('status', 'UNKNOWN')}"
                )

                st.write(
                    f"**Severity:** {severity_value}"
                )

                st.write(
                    f"**Detected:** {incident.get('timestamp', 'N/A')}"
                )

                st.write(
                    f"**Reason:** {incident.get('anomaly_reason', 'N/A')}"
                )

                st.write(
                    f"**Details:** {incident.get('details', 'N/A')}"
                )

            with right:

                st.markdown("### 🤖 AI Analysis")

                analysis = incident.get("analysis")

                if analysis:
                    st.write(analysis)
                else:
                    st.info("Analysis pending.")

            st.markdown("### 📚 RAG Evidence")

            evidence = incident.get("evidence")

            if evidence:
                st.code(evidence)
            else:
                st.info("No RAG evidence available.")


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "Intelligent API Monitoring & Incident Response System • "
    "Hybrid ML + RAG + AI"
)
PY