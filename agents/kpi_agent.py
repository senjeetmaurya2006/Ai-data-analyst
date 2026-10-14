import json
from agents.base import BaseAgent
from analysis.duckdb_engine import DuckDBEngine
from core.models import KPIReport
from workflows.pipeline_context import PipelineContext


class KPIAgent(BaseAgent):
    """Discovers SQL KPI definitions via Gemini and computes exact values via DuckDB."""

    def _execute(self, context: PipelineContext) -> KPIReport:
        profile = context.cleaned_profile
        biz = context.business_context
        schema_info = [
            {"name": c.name, "dtype": c.raw_dtype, "category": c.category.value}
            for c in profile.columns
        ]
        prompt_cfg = self.config.get_prompt("kpi_discovery")
        user_prompt = prompt_cfg["user"].format(
            business_json=biz.model_dump_json(indent=2),
            schema_json=json.dumps(schema_info, indent=2),
        )
        kpi_report = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=KPIReport,
            agent_name=self.name,
        )

        duck_engine = DuckDBEngine(context.working_df)
        for kpi in kpi_report.kpis:
            val = duck_engine.execute_scalar(kpi.sql_query)
            kpi.value = val if val is not None else 0.0
            if kpi.unit == "$":
                kpi.formatted_value = f"${kpi.value:,.2f}"
            elif kpi.unit == "%":
                kpi.formatted_value = f"{kpi.value:,.2f}%"
            else:
                kpi.formatted_value = f"{kpi.value:,.2f} {kpi.unit}".strip()

        context.kpi_report = kpi_report
        return kpi_report
