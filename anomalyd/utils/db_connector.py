import pandas as pd
from sqlalchemy import create_engine, inspect, text

class DBConnector:
    def __init__(self, url, schema=None, connect_args=None):
        self._engine = create_engine(url, connect_args=connect_args or {})

    def get_tables(self):
        return inspect(self._engine).get_table_names()

    def get_row_count(self, table):
        with self._engine.connect() as conn:
            return conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0

    def get_dataframe(self, table):
        return pd.read_sql(f"SELECT * FROM {table}", self._engine)

    def close(self):
        self._engine.dispose()