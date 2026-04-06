from __future__ import annotations

from config import settings
from utils.cache import AgentCache
from utils.llm import call_llm_json, load_prompt
from utils.parser import normalize_validation_output, safe_json_loads


def _cacheable_document_payload(document: dict) -> dict:
    if not isinstance(document, dict):
        return {}
    cacheable = dict(document)
    cacheable.pop("approval", None)
    return cacheable


def run(
    legacy_spec: dict,
    requirements: dict,
    technical_spec: dict,
    generated_files: list[dict],
    logger,
) -> dict:
    payload = {
        "legacy_spec": legacy_spec,
        "requirements": requirements,
        "technical_spec": technical_spec,
        "generated_files": generated_files,
    }
    cache_payload = {
        "legacy_spec": legacy_spec,
        "requirements": _cacheable_document_payload(requirements),
        "technical_spec": _cacheable_document_payload(technical_spec),
        "generated_files": generated_files,
    }
    cache = AgentCache(settings.cache_dir)

    if settings.cache_enabled:
        cached = cache.load("validation", cache_payload)
        if cached:
            logger("validation", "Cache hit for generated target validation.")
            return cached

    logger("validation", "Validating generated target against source behavior and approved design.")
    prompt = load_prompt(settings.prompts_dir / "validation_prompt.txt")
    raw = call_llm_json("validation", prompt, payload, require_live_call=not settings.cache_enabled)
    parsed = safe_json_loads(raw.get("raw_text", ""), fallback=raw)
    normalized = normalize_validation_output(parsed)
    if settings.cache_enabled:
        cache.save("validation", cache_payload, normalized)
    logger("validation", "Generated target validation complete.")
    return normalized
