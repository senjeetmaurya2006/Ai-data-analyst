import duckdb
import polars as pl
from tools.validators import SQLValidator


class DuckDBEngine:
    """Zero-copy SQL execution engine over Polars DataFrames."""

    def __init__(self, df: pl.DataFrame):
        self.df = df
        self.conn = duckdb.connect(database=":memory:")
        self.conn.register("dataset", self.df)

    def execute_scalar(self, sql: str) -> float | None:
        try:
            safe_sql = SQLValidator.validate_readonly_sql(sql)
            res = self.conn.execute(safe_sql).fetchone()
            if res and res[0] is not None:
                return round(float(res[0]), 4)
            return None
        except Exception:
            return None

    def execute_df(self, sql: str) -> pl.DataFrame:
        safe_sql = SQLValidator.validate_readonly_sql(sql)
        return self.conn.execute(safe_sql).pl()
