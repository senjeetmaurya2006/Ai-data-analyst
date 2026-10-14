import json
from agents.base import BaseAgent
from core.models import DashboardLayout
from workflows.pipeline_context import PipelineContext


class DashboardDesignerAgent(BaseAgent):
    """Designs complete 3-row executive dashboard layout JSON."""

    def _execute(self, context: PipelineContext) -> DashboardLayout:
        kpis = context.kpi_report
        viz = context.visualization_report
        prompt_cfg = self.config.get_prompt("dashboard_designer")
        user_prompt = prompt_cfg["user"].format(
            kpi_titles=json.dumps([k.name for k in kpis.kpis]),
            chart_summaries=json.dumps(
                [
                    {"id": c.chart_id, "title": c.title, "type": c.chart_type.value}
                    for c in viz.charts
                ]
            ),
        )
        layout = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=DashboardLayout,
            agent_name=self.name,
        )
        context.dashboard_layout = layout
        return layout
