import polars as pl
from typing import List
from core.models import (
    DatasetProfile,
    DataQualityReport,
    ColumnQualityIssue,
    DataTypeCategory,
)


class DataQualityEngine:
    @staticmethod
    def audit(
        df: pl.DataFrame, profile: DatasetProfile, iqr_multiplier: float = 1.5
    ) -> DataQualityReport:
        issues: List[ColumnQualityIssue] = []
        total_rows = max(df.height, 1)
        total_cells = total_rows * max(df.width, 1)
        total_missing = 0

        dup_count = int(df.is_duplicated().sum())
        dup_pct = round((dup_count / total_rows) * 100.0, 2)

        for col_prof in profile.columns:
            col = col_prof.name
            total_missing += col_prof.null_count

            if col_prof.null_count > 0:
                severity = (
                    "high"
                    if col_prof.null_percentage > 20
                    else ("medium" if col_prof.null_percentage > 5 else "low")
                )
                issues.append(
                    ColumnQualityIssue(
                        column=col,
                        issue_type="missing",
                        severity=severity,
                        affected_rows=col_prof.null_count,
                        affected_percentage=col_prof.null_percentage,
                        details=f"{col_prof.null_count} missing values ({col_prof.null_percentage}%)",
                    )
                )

            if (
                col_prof.category == DataTypeCategory.NUMERIC
                and col_prof.q25 is not None
                and col_prof.q75 is not None
            ):
                iqr = col_prof.q75 - col_prof.q25
                if iqr > 0:
                    lower = col_prof.q25 - iqr_multiplier * iqr
                    upper = col_prof.q75 + iqr_multiplier * iqr
                    outlier_cnt = int(
                        df.filter((pl.col(col) < lower) | (pl.col(col) > upper)).height
                    )
                    if outlier_cnt > 0:
                        out_pct = round((outlier_cnt / total_rows) * 100.0, 2)
                        issues.append(
                            ColumnQualityIssue(
                                column=col,
                                issue_type="outliers",
                                severity="medium" if out_pct > 5 else "low",
                                affected_rows=outlier_cnt,
                                affected_percentage=out_pct,
                                details=f"IQR bounds [{round(lower, 2)}, {round(upper, 2)}] exceeded in {outlier_cnt} rows",
                            )
                        )

            if col_prof.category in (
                DataTypeCategory.TEXT,
                DataTypeCategory.CATEGORICAL,
            ):
                sample_strs = [str(s) for s in col_prof.sample_values if s is not None]
                numeric_like = sum(
                    1
                    for s in sample_strs
                    if s.replace(".", "", 1).replace("-", "", 1).isdigit()
                )
                if len(sample_strs) >= 3 and numeric_like == len(sample_strs):
                    issues.append(
                        ColumnQualityIssue(
                            column=col,
                            issue_type="dtype_issue",
                            severity="medium",
                            affected_rows=total_rows,
                            affected_percentage=100.0,
                            details="Column stored as string but appears numeric.",
                        )
                    )

        missing_penalty = (total_missing / total_cells) * 45.0
        dup_penalty = (dup_count / total_rows) * 25.0
        issue_penalty = min(len(issues) * 2.5, 30.0)
        score = round(
            max(0.0, 100.0 - (missing_penalty + dup_penalty + issue_penalty)), 2
        )

        return DataQualityReport(
            overall_score=score,
            missing_cells_total=total_missing,
            duplicate_rows_count=dup_count,
            duplicate_rows_percentage=dup_pct,
            issues=issues,
            summary=f"Health Score: {score}/100 | Missing Cells: {total_missing} | Duplicate Rows: {dup_count} ({dup_pct}%)",
        )
