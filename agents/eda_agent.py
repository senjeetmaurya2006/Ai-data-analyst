from agents.base import BaseAgent
from analysis.stats_engine import StatsEngine
from core.models import EDAReport
from workflows.pipeline_context import PipelineContext


class EDAAgent(BaseAgent):
    """Performs univariate, bivariate, correlation, trend, and segmentation analysis."""

    def _execute(self, context: PipelineContext) -> EDAReport:
        eda_report = StatsEngine.run_eda(context.working_df, context.cleaned_profile)
        context.eda_report = eda_report
        return eda_report
