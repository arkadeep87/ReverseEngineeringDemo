from __future__ import annotations

from config import settings
from utils.cache import AgentCache
from utils.file_reader import read_folder
from utils.llm import call_llm_json, load_prompt
from utils.parser import normalize_reverse_output, safe_json_loads


CODE_SUFFIXES = {".ts", ".tsx", ".js", ".html"}
SQL_SUFFIXES = {".sql"}


def run(target_folder: str, artifact_kind: str, logger) -> dict:
    prompt_name = "reverse_code_prompt.txt" if artifact_kind == "code" else "reverse_sql_prompt.txt"
    include_suffixes = CODE_SUFFIXES if artifact_kind == "code" else SQL_SUFFIXES

    logger("reverse_target", f"Reading target {artifact_kind} inputs from {target_folder}")
    folder_data = read_folder(
        target_folder,
        max_files=settings.max_files_per_folder,
        max_chars=settings.max_chars_per_file,
        include_suffixes=include_suffixes,
    )
    payload = {"system_name": "Target Insurance System", "artifact_kind": artifact_kind, **folder_data}
    cache = AgentCache(settings.cache_dir)
    cache_key = f"reverse_target_{artifact_kind}_v2"

    if settings.cache_enabled:
        cached = cache.load(cache_key, payload)
        if cached:
            logger("reverse_target", f"Cache hit for target {artifact_kind} reverse engineering.")
            return cached

    logger("reverse_target", f"Calling LLM for target {artifact_kind} reverse engineering.")
    prompt = load_prompt(settings.prompts_dir / prompt_name)
    raw = call_llm_json("reverse_target", prompt, payload, require_live_call=not settings.cache_enabled)
    parsed = safe_json_loads(raw.get("raw_text", ""), fallback=raw)
    normalized = normalize_reverse_output(parsed, system_name="Target Insurance System")
    normalized["read_errors"] = folder_data["errors"]
    if settings.cache_enabled:
        cache.save(cache_key, payload, normalized)
    logger("reverse_target", f"Target {artifact_kind} reverse engineering complete.")
    return normalized
