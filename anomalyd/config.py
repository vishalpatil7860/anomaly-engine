import os
import yaml

class AnomalyConfig:
    def __init__(self, data):
        raw_db = data.get("database", {})
        self.db_url = raw_db.get("url", "sqlite:///anomaly.db")
        self.tables = data.get("tables", [])
        self.storage_path = data.get("storage", {}).get("path", "~/.anomalyd/history.db")
        self.llm_config = data.get("llm", {})

    @classmethod
    def from_file(cls, path):
        path = os.path.expanduser(path)
        with open(path) as f:
            return cls(yaml.safe_load(f) or {})'