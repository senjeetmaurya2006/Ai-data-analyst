from dataclasses import dataclass, field
from typing import Optional, List
import polars as pl
from core.models import (
    DatasetProfile,
    BusinessContext,
    DataQualityReport,
    CleaningPlan,
    CleaningReport,
    EDAReport,
    KPIReport,
    VisualizationReport,
    DashboardLayout,
    InsightReport,
    RootCauseReport,
    VerificationResult,
    RecommendationReport,
    StorytellingReport,
    PipelineArtifacts,
    AgentTrace,
)


@dataclass
class PipelineContext:
    file_path: str
    sheet_name: Optional[str] = None
    user_question: Optional[str] = None
    raw_df: Optional[pl.DataFrame] = None
    working_df: Optional[pl.DataFrame] = None
    dataset_profile: Optional[DatasetProfile] = None
    cleaned_profile: Optional[DatasetProfile] = None
    business_context: Optional[BusinessContext] = None
    quality_report: Optional[DataQualityReport] = None
    cleaning_plan: Optional[CleaningPlan] = None
    cleaning_report: Optional[CleaningReport] = None
    eda_report: Optional[EDAReport] = None
    kpi_report: Optional[KPIReport] = None
    visualization_report: Optional[VisualizationReport] = None
    dashboard_layout: Optional[DashboardLayout] = None
    insight_report: Optional[InsightReport] = None
    root_cause_report: Optional[RootCauseReport] = None
    verification_result: Optional[VerificationResult] = None
    recommendation_report: Optional[RecommendationReport] = None
    storytelling_report: Optional[StorytellingReport] = None
    artifacts: Optional[PipelineArtifacts] = None
    traces: List[AgentTrace] = field(default_factory=list)
