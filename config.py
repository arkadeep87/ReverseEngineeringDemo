from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Settings:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    prompts_dir: Path = field(init=False)
    outputs_dir: Path = field(init=False)
    cache_dir: Path = field(init=False)
    sample_inputs_dir: Path = field(init=False)
    model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    cache_enabled: bool = True
    max_files_per_folder: int = 50
    max_chars_per_file: int = 12000

    def __post_init__(self) -> None:
        self.prompts_dir = self.project_root / "prompts"
        self.outputs_dir = self.project_root / "outputs"
        self.cache_dir = self.outputs_dir / "cache"
        self.sample_inputs_dir = self.project_root / "sample_inputs"
        self.cache_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
