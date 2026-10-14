import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    def __init__(self, config_path: str = "./config/settings.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.raw = yaml.safe_load(f)

        self.prompts_path = self.raw["app"]["prompts_path"]
        with open(self.prompts_path, "r", encoding="utf-8") as f:
            self.prompts = yaml.safe_load(f)

        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.model_name = self.raw["llm"]["model_name"]
        self.temperature = self.raw["llm"]["temperature"]
        self.enable_cache = self.raw["llm"]["enable_cache"]
        self.storage_dir = Path(self.raw["app"]["storage_dir"])
        self.log_dir = Path(self.raw["app"]["log_dir"])

        for sub in ["cache", "outputs", "uploads"]:
            (self.storage_dir / sub).mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def get_prompt(self, key: str) -> dict[str, str]:
        return self.prompts[key]
