import time
import polars as pl
from typing import Tuple, List
from core.models import (
    CleaningPlan,
    CleaningReport,
    CleaningExecutionLog,
    CleaningActionType,
)
from analysis.profiler import DataProfiler
from analysis.quality_engine import DataQualityEngine


class CleaningEngine:
    @staticmethod
    def execute_plan(
        df: pl.DataFrame, plan: CleaningPlan, initial_score: float
    ) -> Tuple[pl.DataFrame, CleaningReport]:
        initial_rows = df.height
        logs: List[CleaningExecutionLog] = []
        working_df = df.clone()

        for op in plan.operations:
            t0 = time.perf_counter()
            rows_before = working_df.height
            col = op.column
            status = "SUCCESS"
            affected = 0

            try:
                if op.action == CleaningActionType.REMOVE_DUPLICATES:
                    working_df = working_df.unique(maintain_order=True)
                    affected = rows_before - working_df.height

                elif col and col in working_df.columns:
                    nulls_before = int(working_df[col].null_count())

                    if op.action == CleaningActionType.MEDIAN_IMPUTATION:
                        if working_df[col].dtype.is_numeric():
                            med = working_df[col].median()
                            if med is not None:
                                working_df = working_df.with_columns(
                                    pl.col(col).fill_null(med)
                                )
                                affected = nulls_before

                    elif op.action == CleaningActionType.MEAN_IMPUTATION:
                        if working_df[col].dtype.is_numeric():
                            mean_val = working_df[col].mean()
                            if mean_val is not None:
                                working_df = working_df.with_columns(
                                    pl.col(col).fill_null(mean_val)
                                )
                                affected = nulls_before

                    elif op.action == CleaningActionType.MODE_IMPUTATION:
                        modes = working_df[col].drop_nulls().mode()
                        if len(modes) > 0:
                            working_df = working_df.with_columns(
                                pl.col(col).fill_null(modes[0])
                            )
                            affected = nulls_before

                    elif op.action == CleaningActionType.ZERO_IMPUTATION:
                        working_df = working_df.with_columns(pl.col(col).fill_null(0))
                        affected = nulls_before

                    elif op.action == CleaningActionType.DROP_MISSING_ROWS:
                        working_df = working_df.drop_nulls(subset=[col])
                        affected = rows_before - working_df.height

                    elif op.action == CleaningActionType.CAP_OUTLIERS_IQR:
                        if working_df[col].dtype.is_numeric():
                            q25 = working_df[col].quantile(0.25)
                            q75 = working_df[col].quantile(0.75)
                            if q25 is not None and q75 is not None:
                                iqr = q75 - q25
                                lower, upper = q25 - 1.5 * iqr, q75 + 1.5 * iqr
                                affected = int(
                                    working_df.filter(
                                        (pl.col(col) < lower) | (pl.col(col) > upper)
                                    ).height
                                )
                                working_df = working_df.with_columns(
                                    pl.col(col).clip(lower, upper)
                                )

                    elif op.action == CleaningActionType.CAST_TO_FLOAT:
                        working_df = working_df.with_columns(
                            pl.col(col).cast(pl.Float64, strict=False)
                        )
                        affected = working_df.height

                    elif op.action == CleaningActionType.CAST_TO_DATETIME:
                        if working_df[col].dtype == pl.String:
                            working_df = working_df.with_columns(
                                pl.col(col).str.to_datetime(strict=False)
                            )
                            affected = working_df.height

                    elif op.action == CleaningActionType.STANDARDIZE_TEXT:
                        if working_df[col].dtype == pl.String:
                            working_df = working_df.with_columns(
                                pl.col(col).str.strip_chars().str.to_titlecase()
                            )
                            affected = working_df.height

            except Exception as exc:
                status = f"SKIPPED ({exc})"

            elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
            logs.append(
                CleaningExecutionLog(
                    operation=op,
                    rows_before=rows_before,
                    rows_after=working_df.height,
                    affected_records=affected,
                    status=status,
                    execution_time_ms=elapsed_ms,
                )
            )

        new_profile = DataProfiler.build_profile(
            working_df, "cleaned", "cleaned", ["cleaned"]
        )
        new_quality = DataQualityEngine.audit(working_df, new_profile)

        report = CleaningReport(
            initial_rows=initial_rows,
            final_rows=working_df.height,
            initial_quality_score=initial_score,
            final_quality_score=new_quality.overall_score,
            logs=logs,
        )
        return working_df, report
