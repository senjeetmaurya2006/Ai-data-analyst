from agents.base import BaseAgent
from core.models import RecommendationReport
from workflows.pipeline_context import PipelineContext


class RecommendationAgent(BaseAgent):
    """Generates Strategic, Tactical, and Immediate Next Action recommendations."""

    def _execute(self, context: PipelineContext) -> RecommendationReport:
        prompt_cfg = self.config.get_prompt("recommendation_engine")
        user_prompt = prompt_cfg["user"].format(
            business_json=context.business_context.model_dump_json(indent=2),
            insights_json=context.insight_report.model_dump_json(indent=2),
            root_causes_json=context.root_cause_report.model_dump_json(indent=2),
        )
        recs = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=RecommendationReport,
            agent_name=self.name,
        )
        context.recommendation_report = recs
        return recs
