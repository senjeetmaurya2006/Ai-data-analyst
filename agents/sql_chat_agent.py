import json
from typing import Any
import polars as pl
from agents.base import BaseAgent
from analysis.duckdb_engine import DuckDBEngine
from core.models import DatasetProfile, NLQueryPlan
from workflows.pipeline_context import PipelineContext


class SQLChatAgent(BaseAgent):
    """Converts natural language questions to DuckDB SQL, executes them, and recommends charts."""

    def answer_question(
        self, df: pl.DataFrame, profile: DatasetProfile, question: str
    ) -> dict[str, Any]:
        schema_info = [
            {"name": c.name, "dtype": c.raw_dtype, "samples": c.sample_values[:3]}
            for c in profile.columns
        ]
        prompt_cfg = self.config.get_prompt("nl_to_sql")
        user_prompt = prompt_cfg["user"].format(
            schema_json=json.dumps(schema_info, indent=2),
            question=question,
        )
        plan: NLQueryPlan = self.brain.generate_structured(
            system_prompt=prompt_cfg["system"],
            user_prompt=user_prompt,
            response_model=NLQueryPlan,
            agent_name=self.name,
        )
        duck = DuckDBEngine(df)
        result_df = duck.execute_df(plan.sql_query)
        return {
            "plan": plan,
            "result_df": result_df,
        }

    def _execute(self, context: PipelineContext) -> Any:
        return self.answer_question(
            context.working_df, context.cleaned_profile, context.user_question or ""
        )
