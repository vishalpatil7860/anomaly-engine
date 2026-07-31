
import numpy as np
import pandas as pd

class DataProfiler:
    def __init__(self, db):
        self.db = db

    def profile_table(self, table):
        df = self.db.get_dataframe(table)
        profiles = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col].dtype):
                profiles[col] = self._numeric(df[col])
            else:
                profiles[col] = self._cat(df[col])
        return profiles

    def _numeric(self, s):
        c = s.dropna()
        if len(c) == 0:
            return None
        q1, q3 = np.percentile(c, [25, 75])
        return {"mean": float(c.mean()), "std": float(c.std()), "q1": float(q1), "q3": float(q3), "min": float(c.min()), "max": float(c.max()), "nulls": int(s.isna().sum())}

    def _cat(self, s):
        c = s.dropna()
        if len(c) == 0:
            return None
        return {"unique": int(c.nunique()), "top": str(c.value_counts().index[0]), "nulls": int(s.isna().sum())}
