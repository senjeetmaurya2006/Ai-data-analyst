from agents.base import BaseAgent
from analysis.quality_engine import DataQualityEngine
from core.models import DataQualityReport
from workflows.pipeline_context import PipelineContext


class DataQualityAgent(BaseAgent):
    """Detects missing values, duplicates, outliers, datatype issues, and computes Quality Score."""

    def _execute(self, context: PipelineContext) -> DataQualityReport:
        report = DataQualityEngine.audit(
            context.working_df,
            context.dataset_profile,
            iqr_multiplier=self.config.raw["data"]["outlier_iqr_multiplier"],
        )
        context.quality_report = report
        return report
