import polars as pl
from typing import Tuple, List
from core.models import DatasetProfile, ColumnProfile, DataTypeCategory
from tools.file_io import FileIOTool


class DataProfiler:
    @staticmethod
    def load_dataset(
        file_path: str, sheet_name: str | None = None
    ) -> Tuple[pl.DataFrame, str, List[str]]:
        return FileIOTool.read_tabular(file_path, sheet_name)

    @staticmethod
    def classify_dtype(
        dtype: pl.DataType, unique_count: int, row_count: int
    ) -> DataTypeCategory:
        if dtype.is_numeric():
            return DataTypeCategory.NUMERIC
        if dtype.is_temporal():
            return DataTypeCategory.DATETIME
        if dtype == pl.Boolean:
            return DataTypeCategory.BOOLEAN
        if unique_count <= max(50, int(row_count * 0.05)):
            return DataTypeCategory.CATEGORICAL
        return DataTypeCategory.TEXT

    @classmethod
    def build_profile(
        cls,
        df: pl.DataFrame,
        filename: str,
        sheet_name: str,
        available_sheets: List[str],
    ) -> DatasetProfile:
        row_count = df.height
        col_count = df.width
        memory_mb = round(df.estimated_size("mb"), 3)
        profiles: List[ColumnProfile] = []

        for col_name in df.columns:
            series = df[col_name]
            dtype = series.dtype
            null_cnt = int(series.null_count())
            null_pct = (
                round((null_cnt / row_count) * 100.0, 2) if row_count > 0 else 0.0
            )
            unique_cnt = int(series.n_unique())
            category = cls.classify_dtype(dtype, unique_cnt, row_count)

            non_null_samples = series.drop_nulls().head(5).to_list()
            is_key = (unique_cnt == row_count) and (null_cnt == 0) and (row_count > 0)

            col_prof = ColumnProfile(
                name=col_name,
                raw_dtype=str(dtype),
                category=category,
                null_count=null_cnt,
                null_percentage=null_pct,
                unique_count=unique_cnt,
                is_unique_key=is_key,
                sample_values=[str(v) for v in non_null_samples],
            )

            if category == DataTypeCategory.NUMERIC and unique_cnt > 0:
                clean_s = series.drop_nulls().cast(pl.Float64)
                if clean_s.len() > 0:
                    col_prof.mean = round(float(clean_s.mean()), 4)
                    col_prof.std = round(float(clean_s.std() or 0.0), 4)
                    col_prof.min_val = round(float(clean_s.min()), 4)
                    col_prof.median = round(float(clean_s.median()), 4)
                    col_prof.max_val = round(float(clean_s.max()), 4)
                    col_prof.q25 = round(float(clean_s.quantile(0.25)), 4)
                    col_prof.q75 = round(float(clean_s.quantile(0.75)), 4)
                    col_prof.skewness = round(float(clean_s.skew() or 0.0), 4)

            profiles.append(col_prof)

        return DatasetProfile(
            filename=filename,
            sheet_name=sheet_name,
            available_sheets=available_sheets,
            row_count=row_count,
            column_count=col_count,
            memory_mb=memory_mb,
            columns=profiles,
        )
