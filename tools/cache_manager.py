import hashlib
import json
from pathlib import Path
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class DiskCacheManager:
    def __init__(self, cache_dir: Path, enabled: bool = True):
        self.cache_dir = cache_dir
        self.enabled = enabled
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def build_key(*parts: str) -> str:
        joined = "||".join(parts)
        return hashlib.sha256(joined.encode("utf-8")).hexdigest()

    def get(self, key: str, model_cls: Type[T]) -> Optional[T]:
        if not self.enabled:
            return None
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return model_cls.model_validate(data)
        return None

    def set(self, key: str, obj: BaseModel) -> None:
        if not self.enabled:
            return
        path = self.cache_dir / f"{key}.json"
        path.write_text(obj.model_dump_json(indent=2), encoding="utf-8")
