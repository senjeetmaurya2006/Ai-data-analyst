from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DataTypeCategory(str, Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    TEXT = "text"


class ColumnProfile(BaseModel):
    name: str
    raw_dtype: str
    category: DataTypeCategory
    null_count: int
    null_percentage: float
    unique_count: int
    is_unique_key: bool
    sample_values: List[Any] = Field(default_factory=list)
    mean: Optional[float] = None
    std: Optional[float] = None
    min_val: Optional[Any] = None
    median: Optional[float] = None
    max_val: Optional[Any] = None
    q25: Optional[float] = None
    q75: Optional[float] = None
    skewness: Optional[float] = None


class DatasetProfile(BaseModel):
    filename: str
    sheet_name: str
    available_sheets: List[str]
    row_count: int
    column_count: int
    memory_mb: float
    columns: List[ColumnProfile]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class DataDictionaryEntry(BaseModel):
    column_name: str
    data_type: str
    description: str
    business_meaning: str
    usage: str


class BusinessContext(BaseModel):
    domain: str
    dataset_purpose: str
    business_objectives: List[str]
    candidate_kpis: List[str]
    primary_time_column: Optional[str] = None
    primary_entity_columns: List[str] = Field(default_factory=list)
    data_dictionary: List[DataDictionaryEntry] = Field(default_factory=list)


class ColumnQualityIssue(BaseModel):
    column: str
    issue_type: str
    severity: str
    affected_rows: int
    affected_percentage: float
    details: str


class DataQualityReport(BaseModel):
    overall_score: float = Field(description="0 to 100 quality score")
    missing_cells_total: int
    duplicate_rows_count: int
    duplicate_rows_percentage: float
    issues: List[ColumnQualityIssue]
    summary: str


class CleaningActionType(str, Enum):
    MEDIAN_IMPUTATION = "median_imputation"
    MEAN_IMPUTATION = "mean_imputation"
    MODE_IMPUTATION = "mode_imputation"
    ZERO_IMPUTATION = "zero_imputation"
    DROP_MISSING_ROWS = "drop_missing_rows"
    REMOVE_DUPLICATES = "remove_duplicates"
    CAP_OUTLIERS_IQR = "cap_outliers_iqr"
    CAST_TO_FLOAT = "cast_to_float"
    CAST_TO_DATETIME = "cast_to_datetime"
    STANDARDIZE_TEXT = "standardize_text"


class CleaningOperation(BaseModel):
    column: Optional[str] = None
    issue: str
    action: CleaningActionType
    rationale: str


class CleaningPlan(BaseModel):
    operations: List[CleaningOperation]


class CleaningExecutionLog(BaseModel):
    operation: CleaningOperation
    rows_before: int
    rows_after: int
    affected_records: int
    status: str
    execution_time_ms: float


class CleaningReport(BaseModel):
    initial_rows: int
    final_rows: int
    initial_quality_score: float
    final_quality_score: float
    logs: List[CleaningExecutionLog]


class KPIDefinition(BaseModel):
    name: str
    category: str
    description: str
    sql_query: str
    unit: str = ""
    value: Optional[float] = None
    formatted_value: Optional[str] = None


class KPIReport(BaseModel):
    kpis: List[KPIDefinition]


class CorrelationPair(BaseModel):
    col_a: str
    col_b: str
    correlation: float


class SegmentMetric(BaseModel):
    dimension: str
    segment_value: str
    metric_col: str
    sum_val: float
    mean_val: float
    share_pct: float


class TrendMetric(BaseModel):
    time_col: str
    metric_col: str
    first_period_val: float
    last_period_val: float
    overall_growth_pct: float
    slope: float


class EDAReport(BaseModel):
    univariate_summary: Dict[str, Dict[str, Any]]
    top_correlations: List[CorrelationPair]
    trends: List[TrendMetric]
    top_segments: List[SegmentMetric]
    bottom_segments: List[SegmentMetric]


class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"


class ChartSpec(BaseModel):
    chart_id: str
    title: str
    chart_type: ChartType
    x_column: str
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    aggregation: Optional[str] = "sum"
    rationale: str


class VisualizationReport(BaseModel):
    charts: List[ChartSpec]


class DashboardLayout(BaseModel):
    row1_kpis: List[str]
    row2_primary_charts: List[str]
    row3_secondary_charts: List[str]


class InsightItem(BaseModel):
    title: str
    category: str
    raw_finding: str
    business_insight: str
    impact_level: str
    confidence_score: float


class InsightReport(BaseModel):
    insights: List[InsightItem]


class RootCauseItem(BaseModel):
    phenomenon: str
    primary_driver: str
    dimension_analyzed: str
    supporting_evidence: str
    impact_weight_pct: float
    rank: int


class RootCauseReport(BaseModel):
    root_causes: List[RootCauseItem]


class VerificationResult(BaseModel):
    is_verified: bool
    audit_notes: List[str]
    verified_insights: List[InsightItem]
    verified_root_causes: List[RootCauseItem]


class RecommendationItem(BaseModel):
    tier: str
    title: str
    action: str
    target_area: str
    expected_impact: str
    priority: int


class RecommendationReport(BaseModel):
    recommendations: List[RecommendationItem]


class StorytellingReport(BaseModel):
    executive_headline: str
    what_happened: str
    why_it_happened: str
    business_impact: str
    risks: str
    opportunities: str
    recommendations_narrative: str
    next_steps: str


class NLQueryPlan(BaseModel):
    sql_query: str
    chart_type: str
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    explanation: str


class AgentTrace(BaseModel):
    agent_name: str
    started_at: str
    completed_at: str
    duration_ms: float
    status: str
    error: Optional[str] = None


class PipelineArtifacts(BaseModel):
    version: str
    pdf_path: str
    pptx_path: str
    html_path: str
