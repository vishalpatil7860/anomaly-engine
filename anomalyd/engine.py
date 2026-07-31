import time
from anomalyd.profiler import DataProfiler
from anomalyd.storage import Storage
from anomalyd.utils.db_connector import DBConnector
from anomalyd.detectors.univariate import UnivariateDetector
from anomalyd.detectors.categorical import CategoricalDriftDetector

class DetectionEngine:
    def __init__(self, config):
        self.config = config
        self.db = DBConnector(config.db_url)
        self.storage = Storage(config.storage_path)
        self.profiler = DataProfiler(self.db)

    def profile(self):
        results = {}
        for tc in self.config.tables:
            table = tc["name"]
            profiles = self.profiler.profile_table(table)
            for col, stats in profiles.items():
                if stats:
                    self.storage.save_baseline(table, col, stats.get("std", "cat"), stats, 0)
            results[table] = {"rows": self.db.get_row_count(table), "cols": len(profiles)}
        return results

    def detect(self):
        results = {}
        for tc in self.config.tables:
            table = tc["name"]
            df = self.db.get_dataframe(table)
            if len(df) == 0:
                continue
            events = []
            det = tc.get("detection", {})
            uv = det.get("univariate", {})
            if uv.get("enabled", True):
                uv["_table"] = table
                events.extend(UnivariateDetector(uv).detect(df))
            cd = det.get("categorical", {})
            if cd.get("enabled", False):
                cd["_table"] = table
                events.extend(CategoricalDriftDetector(cd).detect(df))
            results[table] = events
            if events:
                run_id = self.storage.save_run(table, len(events), "completed")
                for e in events:
                    self.storage.save_anomaly(run_id, e.table, e.column, e.anomaly_type, e.severity, str(e.observed_value), e.expected_range or "", e.explanation or "", e.details)
        return results

    def close(self):
        self.db.close()
        self.storage.close()