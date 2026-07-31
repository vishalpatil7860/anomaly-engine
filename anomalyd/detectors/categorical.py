
import pandas as pd
from anomalyd.detectors import AnomalyEvent, BaseDetector

class CategoricalDriftDetector(BaseDetector):
    type = "categorical"

    def detect(self, df, baseline=None):
        events = []
        table = self.config.get("_table", "")
        for col in self.config.get("columns", []):
            if col not in df.columns:
                continue
            clean = df[col].dropna()
            if len(clean) == 0:
                continue
            vc = clean.value_counts()
            top = vc.index[0]
            top_pct = vc.iloc[0] / len(clean)
            if top_pct > 0.95 and len(vc) > 1:
                events.append(AnomalyEvent(table, col, "dominant", "medium", f"{top} ({top_pct:.1%})", "no single category > 95%", f"Column dominated by {top}", {"top": str(top), "pct": round(top_pct, 4)}))
        return events
