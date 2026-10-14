import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from core.config import AppConfig
from core.llm import GeminiBrain
from core.logger import StructuredAuditLogger
from core.models import AgentTrace
from workflows.pipeline_context import PipelineContext


class BaseAgent(ABC):
    def __init__(
        self,
        name: str,
        config: AppConfig,
        logger: StructuredAuditLogger,
        brain: GeminiBrain | None = None,
    ):
        self.name = name
        self.config = config
        self.logger = logger
        self.brain = brain

    def run(self, context: PipelineContext) -> Any:
        started_at = datetime.utcnow().isoformat()
        t0 = time.perf_counter()
        self.logger.log_event(self.name, "AGENT_START", {})
        try:
            result = self._execute(context)
            duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
            trace = AgentTrace(
                agent_name=self.name,
                started_at=started_at,
                completed_at=datetime.utcnow().isoformat(),
                duration_ms=duration_ms,
                status="COMPLETED",
            )
            context.traces.append(trace)
            self.logger.log_event(
                self.name, "AGENT_COMPLETE", {"duration_ms": duration_ms}
            )
            return result
        except Exception as exc:
            duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
            trace = AgentTrace(
                agent_name=self.name,
                started_at=started_at,
                completed_at=datetime.utcnow().isoformat(),
                duration_ms=duration_ms,
                status="FAILED",
                error=str(exc),
            )
            context.traces.append(trace)
            self.logger.log_event(self.name, "AGENT_ERROR", {"error": str(exc)})
            raise

    @abstractmethod
    def _execute(self, context: PipelineContext) -> Any:
        pass
