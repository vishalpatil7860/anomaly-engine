import sys
from pathlib import Path
from anomalyd.config import AnomalyConfig
from anomalyd.engine import DetectionEngine
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Anomaly Detection Engine", page_icon="triangle", layout="wide")
st.title("Anomaly Detection Engine")
st.caption("Statistical anomaly detection for data pipelines")

def get_engine():
    cp = "anomaly_config.yaml"
    for i, a in enumerate(sys.argv):
        if a == "--config" and i + 1 < len(sys.argv):
            cp = sys.argv[i + 1]
    return DetectionEngine(AnomalyConfig.from_file(cp))

engine = get_engine()

if st.sidebar.button("Run Detection", type="primary", use_container_width=True):
    with st.spinner("Running anomaly detection..."):
        results = engine.detect()
        total = sum(len(v) for v in results.values())
        st.session_state.results = results
        st.session_state.total = total
    st.rerun()

if "results" not in st.session_state:
    st.session_state.results = {}
    st.session_state.total = 0

sm = engine.storage.summary()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Anomalies", sm["total"])
c2.metric("High Severity", sm["high"])

if st.session_state.results:
    st.subheader("Latest Results")
    for table, events in st.session_state.results.items():
        if events:
            df = pd.DataFrame([{"Type": e.anomaly_type, "Column": e.column or "multi", "Severity": e.severity.upper(), "Value": str(e.observed_value)[:50]} for e in events])
            st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Anomaly History")
try:
    anomalies = engine.storage.get_anomalies(100)
    if anomalies:
        df = pd.DataFrame(anomalies)
        df["ts"] = pd.to_datetime(df["ts"])
        df["date"] = df["ts"].dt.date
        daily = df.groupby("date").agg(total=("id", "count")).reset_index()
        fig = px.line(daily, x="date", y="total", title="Anomalies Over Time", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        sev = df["severity"].value_counts()
        fig2 = px.pie(values=sev.values, names=sev.index, title="Severity Distribution")
        st.plotly_chart(fig2, use_container_width=True)
        with st.expander("Recent Anomalies"):
            st.dataframe(df[["ts", "table_name", "anomaly_type", "severity", "observed"]].head(50), use_container_width=True, hide_index=True)
except Exception:
    st.info("Run detection first")

engine.close()