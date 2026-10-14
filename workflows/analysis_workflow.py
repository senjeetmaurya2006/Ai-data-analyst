from typing import Callable, List
from agents.base import BaseAgent
from core.logger import StructuredAuditLogger
from core.exceptions import PipelineExecutionError
from workflows.pipeline_context import PipelineContext


class AnalysisWorkflow:
    def __init__(self, agents: List[BaseAgent], logger: StructuredAuditLogger):
        self.agents = agents
        self.logger = logger

    def register_plugin(self, agent: BaseAgent, position: int | None = None) -> None:
        if position is None:
            self.agents.insert(-1, agent)
        else:
            self.agents.insert(position, agent)

    def execute(
        self,
        context: PipelineContext,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> PipelineContext:
        total = len(self.agents)
        try:
            for idx, agent in enumerate(self.agents):
                if progress_callback:
                    progress_callback(f"Executing {agent.name}...", idx / total)
                agent.run(context)
            if progress_callback:
                progress_callback("All 15 Agents Completed Successfully!", 1.0)
            return context
        except Exception as exc:
            raise PipelineExecutionError(f"Workflow halted at {agent.name}: {exc}") from exc
