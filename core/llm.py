from typing import Type, TypeVar
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai
from google.genai import types
from core.config import AppConfig
from core.logger import StructuredAuditLogger
from core.exceptions import LLMReasoningError
from tools.cache_manager import DiskCacheManager

T = TypeVar("T", bound=BaseModel)


class GeminiBrain:
    """
    Reasoning Engine powered by Gemini via google-genai SDK.
    Includes automatic model fallback (3.1-pro -> 3-flash -> 2.5-flash).
    """

    def __init__(self, config: AppConfig, logger: StructuredAuditLogger):
        self.config = config
        self.logger = logger
        self.cache = DiskCacheManager(
            self.config.storage_dir / "cache", enabled=self.config.enable_cache
        )
        if not self.config.gemini_api_key:
            self.logger.log_event(
                "GeminiBrain",
                "WARNING",
                {"msg": "GEMINI_API_KEY is empty. Set it in .env before running."},
            )
        self.client = genai.Client(api_key=self.config.gemini_api_key or "MISSING_KEY")

        # Build priority list of models to try
        fallback_list = self.config.raw.get("llm", {}).get(
            "fallback_models", ["gemini-3-flash-preview", "gemini-2.5-flash"]
        )
        self.candidate_models = [self.config.model_name] + [
            m for m in fallback_list if m != self.config.model_name
        ]

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=6))
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        agent_name: str = "GeminiBrain",
    ) -> T:
        cache_key = self.cache.build_key(
            self.config.model_name, system_prompt, user_prompt, response_model.__name__
        )
        cached = self.cache.get(cache_key, response_model)
        if cached is not None:
            self.logger.log_event(
                agent_name, "LLM_CACHE_HIT", {"schema": response_model.__name__}
            )
            return cached

        last_error = None
        for model_to_try in self.candidate_models:
            try:
                self.logger.log_event(
                    agent_name,
                    "LLM_CALL_START",
                    {"model": model_to_try, "schema": response_model.__name__},
                )
                response = self.client.models.generate_content(
                    model=model_to_try,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=self.config.temperature,
                        response_mime_type="application/json",
                        response_schema=response_model,
                    ),
                )
                parsed_obj = response_model.model_validate_json(response.text)
                self.cache.set(cache_key, parsed_obj)
                return parsed_obj
            except Exception as exc:
                last_error = exc
                self.logger.log_event(
                    agent_name,
                    "LLM_MODEL_FALLBACK",
                    {"failed_model": model_to_try, "error": str(exc)},
                )

        raise LLMReasoningError(
            f"{agent_name} failed across all candidate models {self.candidate_models}: {last_error}"
        ) from last_error