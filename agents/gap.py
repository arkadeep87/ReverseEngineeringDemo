from __future__ import annotations

from config import settings
from utils.cache import AgentCache
from utils.llm import call_llm_json, load_prompt
from utils.parser import normalize_gap_output, safe_json_loads


def _collect_canonical_rules(*specs: dict) -> list[dict]:
    combined: list[dict] = []
    seen_rule_ids: set[str] = set()
    for spec in specs:
        for item in spec.get("canonical_rules", []):
            if not isinstance(item, dict):
                continue
            rule_id = str(item.get("rule_id", "")).strip()
            if rule_id and rule_id not in seen_rule_ids:
                seen_rule_ids.add(rule_id)
                combined.append(item)
            elif not rule_id:
                combined.append(item)
    return combined


def run(
    legacy_spec: dict,
    target_spec: dict,
    legacy_code_reverse_spec: dict,
    legacy_sql_reverse_spec: dict,
    target_code_reverse_spec: dict,
    target_sql_reverse_spec: dict,
    logger,
) -> dict:
    payload = {
        "legacy_spec": legacy_spec,
        "target_spec": target_spec,
        "legacy_canonical_rules": _collect_canonical_rules(legacy_code_reverse_spec, legacy_sql_reverse_spec),
        "target_canonical_rules": _collect_canonical_rules(target_code_reverse_spec, target_sql_reverse_spec),
        "legacy_reverse_context": {
            "code": legacy_code_reverse_spec,
            "sql": legacy_sql_reverse_spec,
        },
        "target_reverse_context": {
            "code": target_code_reverse_spec,
            "sql": target_sql_reverse_spec,
        },
    }
    prompt = load_prompt(settings.prompts_dir / "gap_prompt.txt")
    cache_payload = {
        **payload,
        "prompt_version": "gap_prompt_numeric_confidence_v2_canonical_rules",
    }
    cache = AgentCache(settings.cache_dir)

    if settings.cache_enabled:
        cached = cache.load("gap", cache_payload)
        if cached:
            logger("gap", "Cache hit for gap analysis.")
            return cached

    logger("gap", "Performing gap analysis.")
    raw = call_llm_json("gap", prompt, payload, require_live_call=not settings.cache_enabled)
    parsed = safe_json_loads(raw.get("raw_text", ""), fallback=raw)
    normalized = normalize_gap_output(parsed)
    if settings.cache_enabled:
        cache.save("gap", cache_payload, normalized)
    logger("gap", "Gap analysis complete.")
    return normalized
