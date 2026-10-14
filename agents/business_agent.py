import json
from agents.base import BaseAgent
from core.models import BusinessContext
from workflows.pipeline_context import PipelineContext


class BusinessUnderstandingAgent(BaseAgent):
    """Infers business domain, objectives, candidate KPIs, and generates Data Dictionary."""

    def _execute(self, context: PipelineContext) -> BusinessContext:
        profile = context.dataset_profile
        prompt_cfg = self.config.get_prompt("business_understanding")
        user_prompt = prompt_cfg["user"].format(
            filename=profile.filename,
            row_count=profile.row_count,
            columns_json=json.dumps([c.model_dump() for c in profile.columns], indent=2),
        )
        biz_context = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=BusinessContext,
            agent_name=self.name,
        )
        context.business_context = biz_context
        return biz_context
