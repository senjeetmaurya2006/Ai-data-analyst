import json
from agents.base import BaseAgent
from core.models import RootCauseReport
from workflows.pipeline_context import PipelineContext


class RootCauseAgent(BaseAgent):
    """Investigates categories, segments, correlations, and trends to rank root causes."""

    def _execute(self, context: PipelineContext) -> RootCauseReport:
        eda = context.eda_report
        drilldown = {
            "correlations": [c.model_dump() for c in eda.top_correlations],
            "top_segments": [s.model_dump() for s in eda.top_segments],
            "bottom_segments": [s.model_dump() for s in eda.bottom_segments],
            "trends": [t.model_dump() for t in eda.trends],
        }
        prompt_cfg = self.config.get_prompt("root_cause_analyzer")
        user_prompt = prompt_cfg["user"].format(
            insights_json=context.insight_report.model_dump_json(indent=2),
            drilldown_json=json.dumps(drilldown, indent=2),
        )
        root_causes = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=RootCauseReport,
            agent_name=self.name,
        )
        context.root_cause_report = root_causes
        return root_causes
