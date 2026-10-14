import polars as pl
from analysis.profiler import DataProfiler
from analysis.quality_engine import DataQualityEngine
from analysis.cleaning_engine import CleaningEngine
from analysis.stats_engine import StatsEngine
from analysis.duckdb_engine import DuckDBEngine
from core.models import CleaningPlan, CleaningOperation, CleaningActionType


def test_engines_end_to_end():
    df = pl.DataFrame(
        {
            "order_id": [1, 2, 2, 3, 4],
            "category": ["Tech", "Office", "Office", "Tech", None],
            "sales": [1200.0, 300.0, 300.0, None, 950.0],
            "profit": [240.0, 45.0, 45.0, 110.0, 190.0],
        }
    )

    profile = DataProfiler.build_profile(df, "test.csv", "default", ["default"])
    assert profile.row_count == 5
    assert profile.column_count == 4

    quality = DataQualityEngine.audit(df, profile)
    assert quality.duplicate_rows_count > 0
    assert quality.missing_cells_total == 2

    plan = CleaningPlan(
        operations=[
            CleaningOperation(
                issue="duplicates",
                action=CleaningActionType.REMOVE_DUPLICATES,
                rationale="Dedup",
            ),
            CleaningOperation(
                column="sales",
                issue="missing",
                action=CleaningActionType.MEDIAN_IMPUTATION,
                rationale="Fill median",
            ),
            CleaningOperation(
                column="category",
                issue="missing",
                action=CleaningActionType.MODE_IMPUTATION,
                rationale="Fill mode",
            ),
        ]
    )

    clean_df, clean_rep = CleaningEngine.execute_plan(df, plan, quality.overall_score)
    assert clean_df.height == 4
    assert int(clean_df["sales"].null_count()) == 0
    assert clean_rep.final_quality_score >= clean_rep.initial_quality_score

    clean_prof = DataProfiler.build_profile(clean_df, "test.csv", "default", ["default"])
    eda = StatsEngine.run_eda(clean_df, clean_prof)
    assert len(eda.top_correlations) >= 1

    duck = DuckDBEngine(clean_df)
    total_sales = duck.execute_scalar('SELECT SUM("sales") FROM dataset')
    assert total_sales is not None and total_sales > 0
