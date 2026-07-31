import json
import os
from datetime import datetime
from sqlalchemy import create_engine, text

class Storage:
    def __init__(self, db_path):
        db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.e = create_engine("sqlite:///" + db_path)
        self._init()

    def _init(self):
        c = self.e.connect()
        for s in [
            "CREATE TABLE IF NOT EXISTS baselines (id INTEGER PRIMARY KEY AUTOINCREMENT, table_name TEXT, column_name TEXT, type TEXT, stats TEXT, rows INTEGER, ts TEXT)",
            "CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY AUTOINCREMENT, table_name TEXT, anomalies INTEGER, status TEXT, ts TEXT)",
            "CREATE TABLE IF NOT EXISTS anomalies (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER, table_name TEXT, column_name TEXT, atype TEXT, severity TEXT, observed TEXT, expected TEXT, explanation TEXT, details TEXT, ts TEXT)",
        ]:
            c.execute(text(s))
        c.commit()
        c.close()

    def save_baseline(self, table, col, btype, stats, rows):
        c = self.e.connect()
        c.execute(text("INSERT OR REPLACE INTO baselines VALUES (NULL,:t,:c,:bt,:s,:r,:ts)"), {"t": table, "c": col, "bt": btype, "s": json.dumps(stats), "r": rows, "ts": datetime.utcnow().isoformat()})
        c.commit()
        c.close()

    def save_run(self, table, anomalies, status):
        c = self.e.connect()
        r = c.execute(text("INSERT INTO runs VALUES (NULL,:t,:a,:s,:ts)"), {"t": table, "a": anomalies, "s": status, "ts": datetime.utcnow().isoformat()})
        c.commit()
        c.close()
        return r.lastrowid

    def get_runs(self, limit):
        c = self.e.connect()
        rows = c.execute(text("SELECT * FROM runs ORDER BY ts DESC LIMIT " + str(limit))).fetchall()
        c.close()
        return [dict(r._mapping) for r in rows]

    def save_anomaly(self, rid, table, col, atype, sev, obs, exp, expl, det):
        c = self.e.connect()
        c.execute(text("INSERT INTO anomalies VALUES (NULL,:rid,:t,:c,:at,:s,:o,:e,:ex,:d,:ts)"), {"rid": rid, "t": table, "c": col, "at": atype, "s": sev, "o": str(obs), "e": exp, "ex": expl, "d": json.dumps(det) if det else None, "ts": datetime.utcnow().isoformat()})
        c.commit()
        c.close()

    def get_anomalies(self, limit):
        c = self.e.connect()
        rows = c.execute(text("SELECT * FROM anomalies ORDER BY ts DESC LIMIT " + str(limit))).fetchall()
        c.close()
        return [dict(r._mapping) for r in rows]

    def summary(self):
        c = self.e.connect()
        t = c.execute(text("SELECT COUNT(*) FROM anomalies")).scalar() or 0
        h = c.execute(text("SELECT COUNT(*) FROM anomalies WHERE severity='high'")).scalar() or 0
        c.close()
        return {"total": t, "high": h}

    def close(self):
        self.e.dispose()