import numpy as np
import polars as pl
from typing import List, Dict, Any
from core.models import (
    DatasetProfile,
    EDAReport,
    CorrelationPair,
    SegmentMetric,
    TrendMetric,
    DataTypeCategory,
)


class StatsEngine:
    @staticmethod
    def run_eda(df: pl.DataFrame, profile: DatasetProfile) -> EDAReport:
        num_cols = [
            c.name for c in profile.columns if c.category == DataTypeCategory.NUMERIC
        ]
        cat_cols = [
            c.name
            for c in profile.columns
            if c.category == DataTypeCategory.CATEGORICAL
        ]
        time_cols = [
            c.name for c in profile.columns if c.category == DataTypeCategory.DATETIME
        ]

        univariate: Dict[str, Dict[str, Any]] = {}
        for c in profile.columns:
            if c.category == DataTypeCategory.NUMERIC:
                univariate[c.name] = {
                    "mean": c.mean,
                    "std": c.std,
                    "median": c.median,
                    "min": c.min_val,
                    "max": c.max_val,
                    "iqr": round((c.q75 or 0) - (c.q25 or 0), 4),
                    "skew": c.skewness,
                }
            elif c.category == DataTypeCategory.CATEGORICAL:
                top_vals = (
                    df.group_by(c.name)
                    .len()
                    .sort("len", descending=True)
                    .head(5)
                    .to_dicts()
                )
                univariate[c.name] = {"unique": c.unique_count, "top_values": top_vals}

        correlations: List[CorrelationPair] = []
        if len(num_cols) >= 2:
            num_df = df.select(num_cols).fill_null(strategy="mean")
            corr_matrix = num_df.corr()
            for i, col_a in enumerate(num_cols):
                for j, col_b in enumerate(num_cols):
                    if j > i:
                        val = corr_matrix[col_b][i]
                        if val is not None and not np.isnan(val):
                            correlations.append(
                                CorrelationPair(
                                    col_a=col_a,
                                    col_b=col_b,
                                    correlation=round(float(val), 4),
                                )
                            )
            correlations.sort(key=lambda x: abs(x.correlation), reverse=True)

        top_segments: List[SegmentMetric] = []
        bottom_segments: List[SegmentMetric] = []
        if cat_cols and num_cols:
            primary_metric = num_cols[0]
            total_metric_sum = float(df[primary_metric].sum() or 1.0)
            for dim in cat_cols[:4]:
                seg_df = (
                    df.group_by(dim)
                    .agg(
                        pl.col(primary_metric).sum().alias("sum_val"),
                        pl.col(primary_metric).mean().alias("mean_val"),
                    )
                    .drop_nulls()
                    .sort("sum_val", descending=True)
                )
                for row in seg_df.head(3).to_dicts():
                    top_segments.append(
                        SegmentMetric(
                            dimension=dim,
                            segment_value=str(row[dim]),
                            metric_col=primary_metric,
                            sum_val=round(float(row["sum_val"] or 0.0), 2),
                            mean_val=round(float(row["mean_val"] or 0.0), 2),
                            share_pct=round(
                                (
                                    float(row["sum_val"] or 0.0)
                                    / max(abs(total_metric_sum), 1e-9)
                                )
                                * 100.0,
                                2,
                            ),
                        )
                    )
                for row in seg_df.tail(2).to_dicts():
                    bottom_segments.append(
                        SegmentMetric(
                            dimension=dim,
                            segment_value=str(row[dim]),
                            metric_col=primary_metric,
                            sum_val=round(float(row["sum_val"] or 0.0), 2),
                            mean_val=round(float(row["mean_val"] or 0.0), 2),
                            share_pct=round(
                                (
                                    float(row["sum_val"] or 0.0)
                                    / max(abs(total_metric_sum), 1e-9)
                                )
                                * 100.0,
                                2,
                            ),
                        )
                    )

        trends: List[TrendMetric] = []
        if time_cols and num_cols:
            t_col = time_cols[0]
            for m_col in num_cols[:3]:
                sorted_df = df.select([t_col, m_col]).drop_nulls().sort(t_col)
                if sorted_df.height >= 2:
                    y_vals = sorted_df[m_col].to_numpy()
                    first_val = float(y_vals[0])
                    last_val = float(y_vals[-1])
                    growth = (
                        ((last_val - first_val) / abs(first_val) * 100.0)
                        if first_val != 0
                        else 0.0
                    )
                    x_idx = np.arange(len(y_vals))
                    slope = (
                        float(np.polyfit(x_idx, y_vals, 1)[0])
                        if len(y_vals) > 1
                        else 0.0
                    )
                    trends.append(
                        TrendMetric(
                            time_col=t_col,
                            metric_col=m_col,
                            first_period_val=round(first_val, 2),
                            last_period_val=round(last_val, 2),
                            overall_growth_pct=round(growth, 2),
                            slope=round(slope, 4),
                        )
                    )

        return EDAReport(
            univariate_summary=univariate,
            top_correlations=correlations[:10],
            trends=trends,
            top_segments=top_segments,
            bottom_segments=bottom_segments,
        )
