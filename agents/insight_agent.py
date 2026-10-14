from agents.base import BaseAgent
from core.models import InsightReport
from workflows.pipeline_context import PipelineContext


class InsightAgent(BaseAgent):
    """Synthesizes KPIs and EDA statistics into quantified business insights."""

    def _execute(self, context: PipelineContext) -> InsightReport:
        prompt_cfg = self.config.get_prompt("insight_generator")
        user_prompt = prompt_cfg["user"].format(
            business_json=context.business_context.model_dump_json(indent=2),
            kpi_json=context.kpi_report.model_dump_json(indent=2),
            eda_json=context.eda_report.model_dump_json(indent=2),
        )
        insights = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=InsightReport,
            agent_name=self.name,
        )
        context.insight_report = insights
        return insights
