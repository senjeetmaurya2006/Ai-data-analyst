from agents.base import BaseAgent
from analysis.cleaning_engine import CleaningEngine
from analysis.profiler import DataProfiler
from core.models import CleaningReport
from workflows.pipeline_context import PipelineContext


class CleaningExecutorAgent(BaseAgent):
    """Executes planned cleaning actions in Polars and records audit metrics."""

    def _execute(self, context: PipelineContext) -> CleaningReport:
        cleaned_df, clean_report = CleaningEngine.execute_plan(
            context.working_df,
            context.cleaning_plan,
            context.quality_report.overall_score,
        )
        context.working_df = cleaned_df
        context.cleaned_profile = DataProfiler.build_profile(
            cleaned_df,
            context.dataset_profile.filename,
            context.dataset_profile.sheet_name,
            context.dataset_profile.available_sheets,
        )
        context.cleaning_report = clean_report
        return clean_report
