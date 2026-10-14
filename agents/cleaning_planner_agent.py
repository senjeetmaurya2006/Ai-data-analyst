from agents.base import BaseAgent
from core.models import CleaningPlan
from workflows.pipeline_context import PipelineContext


class CleaningPlannerAgent(BaseAgent):
    """Uses Gemini to design a deterministic JSON CleaningPlan."""

    def _execute(self, context: PipelineContext) -> CleaningPlan:
        prompt_cfg = self.config.get_prompt("cleaning_planner")
        user_prompt = prompt_cfg["user"].format(
            profile_json=context.dataset_profile.model_dump_json(indent=2),
            quality_json=context.quality_report.model_dump_json(indent=2),
        )
        plan = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=CleaningPlan,
            agent_name=self.name,
        )
        context.cleaning_plan = plan
        return plan
