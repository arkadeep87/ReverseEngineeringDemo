from __future__ import annotations

from config import settings
from utils.cache import AgentCache
from utils.llm import call_llm_json, load_prompt
from utils.parser import normalize_ai_code_review_output, safe_json_loads


def run(
    requirements: dict,
    technical_spec: dict,
    validation_result: dict,
    data_mapping_result: dict,
    generated_diff: list[dict],
    logger,
) -> dict:
    payload = {
        "requirements": requirements,
        "technical_spec": technical_spec,
        "validation_result": validation_result,
        "data_mapping_result": data_mapping_result,
        "generated_diff": generated_diff,
    }
    cache_payload = {
        "requirements": requirements,
        "technical_spec": technical_spec,
        "validation_result": validation_result,
        "data_mapping_result": data_mapping_result,
        "generated_diff": generated_diff,
        "schema_version": "ai_code_review_v1",
    }
    cache = AgentCache(settings.cache_dir)

    if settings.cache_enabled:
        cached = cache.load("ai_code_review_v1", cache_payload)
        if cached:
            logger("ai_code_review", "Cache hit for AI code review.")
            return cached

    logger("ai_code_review", "Generating AI-assisted code review for the forward-engineered diff.")
    prompt = load_prompt(settings.prompts_dir / "ai_code_review_prompt.txt")
    raw = call_llm_json("ai_code_review", prompt, payload, require_live_call=not settings.cache_enabled)
    parsed = safe_json_loads(raw.get("raw_text", ""), fallback=raw)
    normalized = normalize_ai_code_review_output(parsed)
    if settings.cache_enabled:
        cache.save("ai_code_review_v1", cache_payload, normalized)
    logger("ai_code_review", "AI code review complete.")
    return normalized
