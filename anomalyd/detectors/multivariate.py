
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from anomalyd.detectors import AnomalyEvent, BaseDetector

class MultivariateDetector(BaseDetector):
    type = "multivariate"

    def detect(self, df, baseline=None):
        events = []
        table = self.config.get("_table", "")
        cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c].dtype)]
        if len(cols) < 2:
            return events

        data = df[cols].dropna()
        if len(data) < 10:
            return events

        model = IsolationForest(contamination=self.config.get("contamination", 0.01), random_state=42, n_estimators=100)
        preds = model.fit_predict(data)
        scores = model.decision_function(data)

        for idx in np.where(preds == -1)[0][:20]:
            row = data.iloc[idx]
            score = scores[idx]
            sev = "high" if score < np.percentile(scores, 1) else "medium"
            vals = ", ".join(f"{c}={float(row[c]):.2f}" for c in cols[:3])
            events.append(AnomalyEvent(table, None, "multivariate", sev, vals, "decision boundary", f"Score {score:.4f}", {"row": int(idx), "score": round(float(score), 4)}))

        return events