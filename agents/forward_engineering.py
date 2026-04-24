from __future__ import annotations

import json

from config import settings
from utils.cache import AgentCache
from utils.llm import call_llm_json, load_prompt
from utils.parser import normalize_forward_engineering_output, safe_json_loads


def _cacheable_document_payload(document: dict) -> dict:
    if not isinstance(document, dict):
        return {}
    cacheable = dict(document)
    cacheable.pop("approval", None)
    return cacheable


CONFIG_SIGNAL_KEYWORDS = (
    "externaliz",
    "config",
    "configuration",
    "reference data",
    "lookup",
    "rule table",
    "effective dating",
    "effective-dated",
    "versioning",
    "versioned",
    "precedence",
    "fallback",
)

CONFIG_ARTIFACT_KEYWORDS = (
    "config",
    "configuration",
    "reference",
    "lookup",
    "rule",
    "catalog",
)


def _stringify_for_detection(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _requires_config_driven_implementation(requirements: dict, technical_spec: dict) -> bool:
    requirement_sections = [
        requirements.get("functional_requirements", []),
        requirements.get("data_requirements", []),
        requirements.get("migration_requirements", []),
        requirements.get("compliance_requirements", []),
    ]
    text_parts = [_stringify_for_detection(technical_spec.get("rule_configuration_design", []))]
    for section in requirement_sections:
        text_parts.append(_stringify_for_detection(section))
    combined = " ".join(part.lower() for part in text_parts if part)
    return any(keyword in combined for keyword in CONFIG_SIGNAL_KEYWORDS)


def _has_config_artifact(output: dict) -> bool:
    candidate_groups = [
        output.get("postgres_files", []),
        output.get("nodejs_files", []),
        output.get("angular_files", []),
    ]
    for group in candidate_groups:
        for item in group:
            if not isinstance(item, dict):
                continue
            descriptor = " ".join(
                [
                    str(item.get("file_name", "")),
                    str(item.get("purpose", "")),
                    str(item.get("content", ""))[:2000],
                ]
            ).lower()
            if any(keyword in descriptor for keyword in CONFIG_ARTIFACT_KEYWORDS):
                return True
    return False


def _validate_forward_engineering_output(output: dict, requirements: dict, technical_spec: dict) -> None:
    if not _requires_config_driven_implementation(requirements, technical_spec):
        return
    if _has_config_artifact(output):
        return
    raise RuntimeError(
        "Forward engineering output did not include configuration-backed or reference-data-backed rule artifacts even though the approved requirements or technical spec require rule externalization."
    )


def run(requirements: dict, technical_spec: dict, logger) -> dict:
    payload = {"requirements": requirements, "technical_spec": technical_spec}
    cache_payload = {
        "requirements": _cacheable_document_payload(requirements),
        "technical_spec": _cacheable_document_payload(technical_spec),
        "schema_version": "forward_engineering_v2_unit_test_files",
    }
    cache = AgentCache(settings.cache_dir)

    if settings.cache_enabled:
        cached = cache.load("forward_engineering_v2_unit_test_files", cache_payload)
        if cached:
            logger("forward_engineering", "Cache hit for forward engineering output.")
            return cached

    logger("forward_engineering", "Generating forward engineering artifacts from approved inputs.")
    prompt = load_prompt(settings.prompts_dir / "forward_engineering_prompt.txt")
    raw = call_llm_json("forward_engineering", prompt, payload, require_live_call=not settings.cache_enabled)
    parsed = safe_json_loads(raw.get("raw_text", ""), fallback=raw)
    normalized = normalize_forward_engineering_output(parsed)
    _validate_forward_engineering_output(normalized, requirements, technical_spec)
    if settings.cache_enabled:
        cache.save("forward_engineering_v2_unit_test_files", cache_payload, normalized)
    logger("forward_engineering", "Forward engineering artifact generation complete.")
    return normalized
