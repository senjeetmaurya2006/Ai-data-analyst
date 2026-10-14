from pathlib import Path
import pandas as pd
import polars as pl
from typing import Tuple, List
from core.exceptions import UnsupportedFileFormatError


class FileIOTool:
    SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

    @classmethod
    def validate_path(cls, file_path: str) -> Path:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileFormatError(
                f"Extension '{path.suffix}' not supported. Use CSV or XLSX."
            )
        return path

    @classmethod
    def read_tabular(
        cls, file_path: str, sheet_name: str | None = None
    ) -> Tuple[pl.DataFrame, str, List[str]]:
        path = cls.validate_path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".csv":
            df = pl.read_csv(
                str(path),
                infer_schema_length=10000,
                ignore_errors=True,
                try_parse_dates=True,
            )
            return df, "csv_default", ["csv_default"]

        excel_file = pd.ExcelFile(str(path))
        sheets = list(excel_file.sheet_names)
        target_sheet = sheet_name if (sheet_name and sheet_name in sheets) else sheets[0]
        try:
            df = pl.read_excel(str(path), sheet_name=target_sheet)
        except Exception:
            pdf = pd.read_excel(str(path), sheet_name=target_sheet)
            df = pl.from_pandas(pdf)
        return df, target_sheet, sheets
