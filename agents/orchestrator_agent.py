from typing import Callable
from core.config import AppConfig
from core.llm import GeminiBrain
from core.logger import StructuredAuditLogger
from agents.base import BaseAgent
from agents.file_agent import FileAgent
from agents.business_agent import BusinessUnderstandingAgent
from agents.data_quality_agent import DataQualityAgent
from agents.cleaning_planner_agent import CleaningPlannerAgent
from agents.cleaning_executor_agent import CleaningExecutorAgent
from agents.eda_agent import EDAAgent
from agents.kpi_agent import KPIAgent
from agents.visualization_agent import VisualizationAgent
from agents.dashboard_designer_agent import DashboardDesignerAgent
from agents.insight_agent import InsightAgent
from agents.root_cause_agent import RootCauseAgent
from agents.verification_agent import InsightVerificationAgent
from agents.recommendation_agent import RecommendationAgent
from agents.storytelling_agent import StorytellingAgent
from agents.report_agent import ReportAgent
from agents.sql_chat_agent import SQLChatAgent
from workflows.pipeline_context import PipelineContext
from workflows.analysis_workflow import AnalysisWorkflow


class OrchestratorAgent:
    """
    Agent 1: Master Orchestrator coordinating the 15-agent DAG workflow and plugins.
    """

    def __init__(self, config: AppConfig | None = None):
        self.config = config or AppConfig()
        self.logger = StructuredAuditLogger(self.config.log_dir)
        self.brain = GeminiBrain(self.config, self.logger)

        self.agents: list[BaseAgent] = [
            FileAgent("FileAgent", self.config, self.logger),
            BusinessUnderstandingAgent(
                "BusinessUnderstandingAgent", self.config, self.logger, self.brain
            ),
            DataQualityAgent("DataQualityAgent", self.config, self.logger),
            CleaningPlannerAgent(
                "CleaningPlannerAgent", self.config, self.logger, self.brain
            ),
            CleaningExecutorAgent("CleaningExecutorAgent", self.config, self.logger),
            EDAAgent("EDAAgent", self.config, self.logger),
            KPIAgent("KPIAgent", self.config, self.logger, self.brain),
            VisualizationAgent(
                "VisualizationAgent", self.config, self.logger, self.brain
            ),
            DashboardDesignerAgent(
                "DashboardDesignerAgent", self.config, self.logger, self.brain
            ),
            InsightAgent("InsightAgent", self.config, self.logger, self.brain),
            RootCauseAgent("RootCauseAgent", self.config, self.logger, self.brain),
            InsightVerificationAgent(
                "InsightVerificationAgent", self.config, self.logger, self.brain
            ),
            RecommendationAgent(
                "RecommendationAgent", self.config, self.logger, self.brain
            ),
            StorytellingAgent("StorytellingAgent", self.config, self.logger, self.brain),
            ReportAgent("ReportAgent", self.config, self.logger),
        ]
        self.workflow = AnalysisWorkflow(self.agents, self.logger)
        self.sql_chat_agent = SQLChatAgent(
            "SQLChatAgent", self.config, self.logger, self.brain
        )

    def register_plugin_agent(
        self, agent: BaseAgent, position: int | None = None
    ) -> None:
        self.workflow.register_plugin(agent, position)

    def run_full_pipeline(
        self,
        file_path: str,
        sheet_name: str | None = None,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> PipelineContext:
        ctx = PipelineContext(file_path=file_path, sheet_name=sheet_name)
        return self.workflow.execute(ctx, progress_callback=progress_callback)
