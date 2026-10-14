from agents.base import BaseAgent
from core.models import VerificationResult, InsightReport, RootCauseReport
from workflows.pipeline_context import PipelineContext


class InsightVerificationAgent(BaseAgent):
    """Second AI agent that verifies insights and root causes against ground-truth math."""

    def _execute(self, context: PipelineContext) -> VerificationResult:
        prompt_cfg = self.config.get_prompt("insight_verifier")
        user_prompt = prompt_cfg["user"].format(
            kpi_json=context.kpi_report.model_dump_json(indent=2),
            eda_json=context.eda_report.model_dump_json(indent=2),
            insights_json=context.insight_report.model_dump_json(indent=2),
            root_causes_json=context.root_cause_report.model_dump_json(indent=2),
        )
        verification = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=VerificationResult,
            agent_name=self.name,
        )
        context.insight_report = InsightReport(insights=verification.verified_insights)
        context.root_cause_report = RootCauseReport(
            root_causes=verification.verified_root_causes
        )
        context.verification_result = verification
        return verification
