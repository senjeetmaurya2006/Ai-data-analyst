from pathlib import Path
from agents.base import BaseAgent
from analysis.profiler import DataProfiler
from core.models import DatasetProfile
from workflows.pipeline_context import PipelineContext


class FileAgent(BaseAgent):
    """Reads CSV/XLSX, detects sheets, schemas, datatypes, and generates DatasetProfile."""

    def _execute(self, context: PipelineContext) -> DatasetProfile:
        df, active_sheet, all_sheets = DataProfiler.load_dataset(
            context.file_path, context.sheet_name
        )
        context.raw_df = df
        context.working_df = df
        profile = DataProfiler.build_profile(
            df, Path(context.file_path).name, active_sheet, all_sheets
        )
        context.dataset_profile = profile
        return profile
