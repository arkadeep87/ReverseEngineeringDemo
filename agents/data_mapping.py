from __future__ import annotations

from config import settings
from agents import collate, reverse_target
from utils.cache import AgentCache
from utils.file_reader import read_folder
from utils.llm import call_llm_json, load_prompt
from utils.parser import normalize_data_mapping_output, safe_json_loads


def run(
    legacy_spec: dict,
    target_spec: dict,
    generated_code_folder: str,
    generated_sql_folder: str,
    legacy_data_dictionary_folder: str,
    target_data_dictionary_folder: str,
    logger,
) -> dict:
    logger("data_mapping", "Reverse engineering forward-engineered target code artifacts.")
    forward_engineered_code_reverse_spec = reverse_target.run(
        generated_code_folder,
        "code",
        lambda a, m: logger("data_mapping", f"{a}: {m}"),
    )

    logger("data_mapping", "Reverse engineering forward-engineered target SQL artifacts.")
    forward_engineered_sql_reverse_spec = reverse_target.run(
        generated_sql_folder,
        "sql",
        lambda a, m: logger("data_mapping", f"{a}: {m}"),
    )

    logger("data_mapping", "Collating forward-engineered target specifications.")
    forward_engineered_target_spec = collate.run(
        "Forward Engineered Target System",
        forward_engineered_code_reverse_spec,
        forward_engineered_sql_reverse_spec,
        lambda _a, m: logger("data_mapping", m),
    )

    logger("data_mapping", "Reading legacy and initial target data dictionary inputs.")
    legacy_data_dictionary = read_folder(
        legacy_data_dictionary_folder,
        max_files=settings.max_files_per_folder,
        max_chars=settings.max_chars_per_file,
    )
    target_data_dictionary = read_folder(
        target_data_dictionary_folder,
        max_files=settings.max_files_per_folder,
        max_chars=settings.max_chars_per_file,
    )

    payload = {
        "legacy_spec": legacy_spec,
        "target_spec": target_spec,
        "forward_engineered_code_reverse_spec": forward_engineered_code_reverse_spec,
        "forward_engineered_sql_reverse_spec": forward_engineered_sql_reverse_spec,
        "forward_engineered_target_spec": forward_engineered_target_spec,
        "legacy_data_dictionary": legacy_data_dictionary,
        "target_data_dictionary": target_data_dictionary,
    }
    cache_payload = {**payload, "prompt_version": "data_mapping_v2_column_mapping_reconciliation"}
    cache = AgentCache(settings.cache_dir)

    if settings.cache_enabled:
        cached = cache.load("data_mapping", cache_payload)
        if cached:
            logger("data_mapping", "Cache hit for final data mapping analysis.")
            return cached

    logger("data_mapping", "Generating final data mapping analysis.")
    prompt = load_prompt(settings.prompts_dir / "data_mapping_prompt.txt")
    raw = call_llm_json("data_mapping", prompt, payload, require_live_call=not settings.cache_enabled)
    parsed = safe_json_loads(raw.get("raw_text", ""), fallback=raw)
    normalized_mapping = normalize_data_mapping_output(parsed)
    result = {
        "forward_engineered_code_reverse_spec": forward_engineered_code_reverse_spec,
        "forward_engineered_sql_reverse_spec": forward_engineered_sql_reverse_spec,
        "forward_engineered_target_spec": forward_engineered_target_spec,
        "legacy_data_dictionary": legacy_data_dictionary,
        "target_data_dictionary": target_data_dictionary,
        "mapping_analysis": normalized_mapping,
    }

    if settings.cache_enabled:
        cache.save("data_mapping", cache_payload, result)

    logger("data_mapping", "Final data mapping analysis complete.")
    return result
