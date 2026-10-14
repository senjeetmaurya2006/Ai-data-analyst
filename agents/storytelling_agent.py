from agents.base import BaseAgent
from core.models import StorytellingReport
from workflows.pipeline_context import PipelineContext


class StorytellingAgent(BaseAgent):
    """Creates a 7-part consulting-style executive narrative."""

    def _execute(self, context: PipelineContext) -> StorytellingReport:
        prompt_cfg = self.config.get_prompt("storytelling_engine")
        user_prompt = prompt_cfg["user"].format(
            business_json=context.business_context.model_dump_json(indent=2),
            kpi_json=context.kpi_report.model_dump_json(indent=2),
            insights_json=context.insight_report.model_dump_json(indent=2),
            root_causes_json=context.root_cause_report.model_dump_json(indent=2),
            recommendations_json=context.recommendation_report.model_dump_json(indent=2),
        )
        story = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=StorytellingReport,
            agent_name=self.name,
        )
        context.storytelling_report = story
        return story
