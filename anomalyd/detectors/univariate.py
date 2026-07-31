import numpy as np
import pandas as pd
from anomalyd.detectors import AnomalyEvent, BaseDetector

class UnivariateDetector(BaseDetector):
    type = "univariate"

    def detect(self, df, baseline=None):
        events = []
        method = self.config.get("method", "zscore")
        threshold = self.config.get("threshold", 3.0)
        table = self.config.get("_table", "")

        for col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col].dtype):
                continue
            clean = df[col].dropna()
            if len(clean) < 3:
                continue

            if method == "zscore":
                mean, std = clean.mean(), clean.std()
                if std == 0:
                    continue
                z = np.abs((clean - mean) / std)
                for idx in z[z > threshold].index:
                    sev = "high" if z[idx] > threshold * 1.5 else "medium"
                    events.append(AnomalyEvent(table, col, "zscore", sev, float(clean[idx]), f"mean={mean:.2f}", f"Z-score {z[idx]:.2f}", {"z": round(float(z[idx]), 2)}))

            elif method == "iqr":
                q1, q3 = clean.quantile(0.25), clean.quantile(0.75)
                iqr = q3 - q1
                low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                for idx in clean[(clean < low) | (clean > high)].index:
                    v = float(clean[idx])
                    sev = "high" if v < q1 - 3 * iqr or v > q3 + 3 * iqr else "medium"
                    events.append(AnomalyEvent(table, col, "iqr", sev, v, f"[{low:.2f}, {high:.2f}]", "Outside IQR bounds", {"q1": float(q1), "q3": float(q3)}))

        return events