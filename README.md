# Anomaly Detection Engine

Free, open-source data anomaly detection system for data engineers. Profiles database tables, builds statistical baselines, detects anomalies using univariate (zscore/IQR/MAD), time series (Prophet), multivariate (Isolation Forest), and categorical drift. CLI + Streamlit dashboard + optional local LLM explanations.

## Quick Start
```bash
pip install -r requirements.txt
cp examples/example_config.yaml anomaly_config.yaml
python -m anomalyd.cli profile
python -m anomalyd.cli detect
```

All dependencies are free and open-source.