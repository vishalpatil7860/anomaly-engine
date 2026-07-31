import warnings
warnings.filterwarnings("ignore")
import pandas as pd
from prophet import Prophet
from anomalyd.detectors import AnomalyEvent, BaseDetector

class TimeSeriesDetector(BaseDetector):
    type = "timeseries"

    def detect(self, df, baseline=None):
        events = []
        table = self.config.get("_table", "")
        ts_col = self.config.get("timestamp_column", "timestamp")
        metrics = self.config.get("metric_columns", [])

        if ts_col not in df.columns:
            return events

        for metric in metrics:
            if metric not in df.columns:
                continue
            clean = df[[ts_col, metric]].dropna()
            clean.columns = ["ds", "y"]
            clean["ds"] = pd.to_datetime(clean["ds"], errors="coerce")
            clean = clean.dropna()

            if len(clean) < 10:
                continue

            try:
                m = Prophet(interval_width=0.95)
                m.fit(clean)
                forecast = m.predict(clean[["ds"]])
                merged = clean.merge(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]], on="ds")
                bad = merged[(merged["y"] < merged["yhat_lower"]) | (merged["y"] > merged["yhat_upper"])]

                for _, row in bad.iterrows():
                    actual = float(row["y"])
                    lower = float(row["yhat_lower"])
                    upper = float(row["yhat_upper"])
                    dev = (actual - float(row["yhat"])) / float(row["yhat"]) * 100 if float(row["yhat"]) != 0 else 0
                    sev = "high" if abs(dev) > 100 else "medium"
                    events.append(AnomalyEvent(table, metric, "timeseries", sev, actual, f"[{lower:.2f}, {upper:.2f}]", f"Deviation {dev:+.1f}%", {"lower": round(lower, 2), "upper": round(upper, 2), "dev_pct": round(dev, 2)}))
            except Exception:
                pass

        return events