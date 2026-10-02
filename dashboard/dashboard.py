import pandas as pd
import plotly.express as px
import streamlit as st

from app.db import init_db
from app.monitoring.store import recent
from app.incidents.manager import recent as incidents


st.set_page_config(
    page_title="Intelligent API Monitoring",
    page_icon="⚡",
    layout="wide",
)

init_db()

st.title("⚡ Intelligent API Monitoring & Incident Response")
st.caption(
    "Real-time monitoring • Hybrid anomaly detection • Incident management • RAG-assisted analysis"
)

# -----------------------------
# Load data
# -----------------------------
metrics = pd.DataFrame(recent(1000))
incidents_df = pd.DataFrame(incidents(200))

if not metrics.empty:
    metrics["timestamp"] = pd.to_datetime(metrics["timestamp"])

# -----------------------------
# KPI cards
# -----------------------------
total_metrics = len(metrics)

open_incidents = (
    int((incidents_df["status"] == "OPEN").sum())
    if not incidents_df.empty
    else 0
)

anomalies = (
    int(metrics["is_anomaly"].sum())
    if not metrics.empty and "is_anomaly" in metrics.columns
    else 0
)

targets = (
    int(metrics["target"].nunique())
    if not metrics.empty
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 Metrics", total_metrics)
col2.metric("🚨 Open Incidents", open_incidents)
col3.metric("⚠️ Anomalies", anomalies)
col4.metric("🎯 Targets", targets)

st.divider()

# -----------------------------
# Endpoint health
# -----------------------------
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

    health_cols = st.columns(min(len(latest), 5))

    for idx, (_, row) in enumerate(latest.iterrows()):
        if idx >= 5:
            break

        target_name = row["target"].split("/")[-1] or "root"

        if row["success"]:
            status = "🟢 HEALTHY"
        else:
            status = "🔴 FAILED"

        health_cols[idx].markdown(
            f"""
**`/{target_name}`**

{status}

Latency: **{row['latency_ms']:.1f} ms**

HTTP: **{row['status_code']}**
"""
        )

st.divider()

# -----------------------------
# Charts
# -----------------------------
if not metrics.empty:

    chart1, chart2 = st.columns(2)

    with chart1:
        st.subheader("📈 Latency")

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

    with chart2:
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

# -----------------------------
# Incident overview
# -----------------------------
st.divider()
st.subheader("🚨 Incident Overview")

if incidents_df.empty:
    st.success("No incidents recorded.")
else:

    ic1, ic2 = st.columns(2)

    with ic1:
        severity_counts = (
            incidents_df["severity"]
            .value_counts()
            .reset_index()
        )

        severity_counts.columns = ["severity", "count"]

        fig = px.bar(
            severity_counts,
            x="severity",
            y="count",
            text="count",
            labels={
                "severity": "Severity",
                "count": "Incidents",
            },
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with ic2:
        status_counts = (
            incidents_df["status"]
            .value_counts()
            .reset_index()
        )

        status_counts.columns = ["status", "count"]

        fig = px.pie(
            status_counts,
            names="status",
            values="count",
            hole=0.45,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

# -----------------------------
# Recent metrics
# -----------------------------
st.divider()
st.subheader("📋 Recent Metrics")

if metrics.empty:
    st.info("No monitoring metrics available.")
else:
    display_cols = [
        "timestamp",
        "target",
        "latency_ms",
        "status_code",
        "success",
        "error_rate",
        "throughput",
    ]

    available_cols = [
        c for c in display_cols
        if c in metrics.columns
    ]

    st.dataframe(
        metrics.sort_values(
            "timestamp",
            ascending=False,
        ).head(100)[available_cols],
        use_container_width=True,
        hide_index=True,
    )

# -----------------------------
# Incidents
# -----------------------------
st.divider()
st.subheader("🔎 Incident Details")

if incidents_df.empty:
    st.success("No incidents recorded yet.")
else:

    for _, row in incidents_df.head(30).iterrows():

        severity_value = row["severity"]

        if severity_value == "CRITICAL":
            icon = "🔴"
        elif severity_value == "HIGH":
            icon = "🟠"
        elif severity_value == "MEDIUM":
            icon = "🟡"
        else:
            icon = "🔵"

        with st.expander(
            f"{icon} {severity_value} | "
            f"{row['incident_id']} | "
            f"{row['target']}"
        ):

            left, right = st.columns(2)

            with left:
                st.markdown("### Incident")

                st.write(
                    f"**Status:** {row['status']}"
                )

                st.write(
                    f"**Reason:** {row['anomaly_reason']}"
                )

                st.write(
                    f"**Details:** {row['details']}"
                )

            with right:
                st.markdown("### Detection")

                st.write(
                    f"**Anomaly Score:** {row['anomaly_score']}"
                )

                st.write(
                    f"**Timestamp:** {row['timestamp']}"
                )

            st.markdown("### 🤖 Incident Analysis")

            st.write(
                row["analysis"]
                if row["analysis"]
                else "Analysis pending."
            )

            st.markdown("### 📚 RAG Evidence")

            evidence = row["evidence"]

            if evidence:
                st.code(evidence)
            else:
                st.info("No evidence recorded.")

# -----------------------------
# Footer
# -----------------------------
st.divider()

st.caption(
    "Intelligent API Monitoring & Incident Response System • "
    "Hybrid Detection + RAG + AI-assisted Incident Analysis"
)
