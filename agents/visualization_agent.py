import json
from agents.base import BaseAgent
from core.models import VisualizationReport
from workflows.pipeline_context import PipelineContext


class VisualizationAgent(BaseAgent):
    """Selects optimal chart types and specifications automatically."""

    def _execute(self, context: PipelineContext) -> VisualizationReport:
        profile = context.cleaned_profile
        biz = context.business_context
        eda = context.eda_report

        schema_info = [
            {"name": c.name, "category": c.category.value, "unique": c.unique_count}
            for c in profile.columns
        ]
        prompt_cfg = self.config.get_prompt("visualization_recommender")
        user_prompt = prompt_cfg["user"].format(
            schema_json=json.dumps(schema_info, indent=2),
            objectives_json=json.dumps(biz.business_objectives),
            eda_json=eda.model_dump_json(indent=2),
        )
        viz_report = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=VisualizationReport,
            agent_name=self.name,
        )
        context.visualization_report = viz_report
        return viz_report
