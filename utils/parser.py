from __future__ import annotations

import json
import re
from typing import Any


def extract_json_candidate(text: str) -> str:
    fenced_match = re.search(r"```json\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced_match:
        return fenced_match.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def safe_json_loads(text: str, fallback: dict[str, Any]) -> dict[str, Any]:
    candidate = extract_json_candidate(text)
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    return fallback


def ensure_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def ensure_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def normalize_reverse_output(payload: dict[str, Any], system_name: str) -> dict[str, Any]:
    return {
        "system_name": payload.get("system_name") or system_name,
        "artifact_kind": payload.get("artifact_kind", ""),
        "summary": payload.get("summary", ""),
        "fields": ensure_list(payload.get("fields")),
        "business_rules": ensure_list(payload.get("business_rules")),
        "canonical_rules": ensure_list(payload.get("canonical_rules")),
        "country_specific_rules": ensure_list(payload.get("country_specific_rules")),
        "validations": ensure_list(payload.get("validations")),
        "calculations": ensure_list(payload.get("calculations")),
        "ui_components": ensure_list(payload.get("ui_components")),
        "classes": ensure_list(payload.get("classes")),
        "methods": ensure_list(payload.get("methods")),
        "procedures": ensure_list(payload.get("procedures")),
        "procedure_dependencies": ensure_list(payload.get("procedure_dependencies")),
        "table_dependencies": ensure_list(payload.get("table_dependencies")),
        "api_endpoints": ensure_list(payload.get("api_endpoints")),
        "confidence": payload.get("confidence", {}),
        "source_files": ensure_list(payload.get("source_files")),
        "notes": ensure_list(payload.get("notes")),
    }


def normalize_system_output(payload: dict[str, Any], system_name: str) -> dict[str, Any]:
    normalized = normalize_reverse_output(payload, system_name=system_name)
    normalized["transaction_flow"] = ensure_list(payload.get("transaction_flow"))
    normalized["entities"] = ensure_list(payload.get("entities"))
    normalized["integrations"] = ensure_list(payload.get("integrations"))
    normalized["persistence_model"] = ensure_list(payload.get("persistence_model"))
    normalized["audit_controls"] = ensure_list(payload.get("audit_controls"))
    normalized["exception_paths"] = ensure_list(payload.get("exception_paths"))
    normalized["flow_map"] = payload.get("flow_map", {"nodes": [], "edges": [], "diagram_text": ""})
    normalized["source_breakdown"] = payload.get("source_breakdown", {})
    return normalized


def normalize_gap_output(payload: dict[str, Any]) -> dict[str, Any]:
    confidence = payload.get("confidence", {})
    return {
        "missing_features": ensure_list(payload.get("missing_features")),
        "incorrect_implementations": ensure_list(payload.get("incorrect_implementations")),
        "compliance_gaps": ensure_list(payload.get("compliance_gaps")),
        "risks": ensure_list(payload.get("risks")),
        "rule_comparison": ensure_list(payload.get("rule_comparison")),
        "common_rules_missed": ensure_list(payload.get("common_rules_missed")),
        "country_specific_rules_missed": ensure_list(payload.get("country_specific_rules_missed")),
        "confidence": {
            "gap_confidence": ensure_float(confidence.get("gap_confidence", 0.0)),
            "coverage_of_analysis": confidence.get("coverage_of_analysis", {}),
            "notes": ensure_list(confidence.get("notes")),
        },
    }


def normalize_forward_engineering_output(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_type": payload.get("document_type", "forward_engineering_output"),
        "angular_files": ensure_list(payload.get("angular_files")),
        "angular_test_files": ensure_list(payload.get("angular_test_files")),
        "nodejs_files": ensure_list(payload.get("nodejs_files")),
        "nodejs_test_files": ensure_list(payload.get("nodejs_test_files")),
        "postgres_files": ensure_list(payload.get("postgres_files")),
        "test_cases": ensure_list(payload.get("test_cases")),
        "generation_notes": ensure_list(payload.get("generation_notes")),
        "traceability_summary": ensure_list(payload.get("traceability_summary")),
    }


def normalize_validation_output(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    confidence = payload.get("confidence", {})
    return {
        "summary": {
            "overall_status": summary.get("overall_status", "unknown"),
            "sync_score": ensure_float(summary.get("sync_score", 0.0)),
            "difference_count": int(ensure_float(summary.get("difference_count", 0))),
            "suggestion_count": int(ensure_float(summary.get("suggestion_count", 0))),
            "notes": ensure_list(summary.get("notes")),
        },
        "differences": ensure_list(payload.get("differences")),
        "suggestions": ensure_list(payload.get("suggestions")),
        "confidence": {
            "validation_confidence": ensure_float(confidence.get("validation_confidence", 0.0)),
            "notes": ensure_list(confidence.get("notes")),
        },
    }


def normalize_data_mapping_output(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    confidence = payload.get("confidence", {})
    field_mappings = []
    for item in ensure_list(payload.get("field_mappings")):
        if isinstance(item, dict):
            normalized_item = dict(item)
            normalized_item["data_mapping_rule"] = normalized_item.get("data_mapping_rule") or normalized_item.get("transformation_logic", "")
            field_mappings.append(normalized_item)
        else:
            field_mappings.append(item)
    return {
        "summary": {
            "overall_mapping_status": summary.get("overall_mapping_status", "unknown"),
            "mapping_coverage": ensure_float(summary.get("mapping_coverage", 0.0)),
            "legacy_entities_reviewed": int(ensure_float(summary.get("legacy_entities_reviewed", 0))),
            "final_entities_reviewed": int(ensure_float(summary.get("final_entities_reviewed", 0))),
            "mapped_columns_count": int(ensure_float(summary.get("mapped_columns_count", 0))),
            "unmapped_columns_count": int(ensure_float(summary.get("unmapped_columns_count", 0))),
            "transformation_count": int(ensure_float(summary.get("transformation_count", 0))),
            "reconciliation_rule_count": int(ensure_float(summary.get("reconciliation_rule_count", 0))),
            "key_findings": ensure_list(summary.get("key_findings")),
        },
        "field_mappings": field_mappings,
        "reconciliation_approach": ensure_list(payload.get("reconciliation_approach")),
        "reference_data_mappings": ensure_list(payload.get("reference_data_mappings")),
        "unmapped_legacy_fields": ensure_list(payload.get("unmapped_legacy_fields")),
        "new_final_state_fields": ensure_list(payload.get("new_final_state_fields")),
        "transformations": ensure_list(payload.get("transformations")),
        "data_quality_risks": ensure_list(payload.get("data_quality_risks")),
        "migration_notes": ensure_list(payload.get("migration_notes")),
        "confidence": {
            "mapping_confidence": ensure_float(confidence.get("mapping_confidence", 0.0)),
            "notes": ensure_list(confidence.get("notes")),
        },
    }


def normalize_ai_code_review_output(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    return {
        "summary": {
            "overall_recommendation": summary.get("overall_recommendation", "comment"),
            "risk_level": summary.get("risk_level", "medium"),
            "total_findings": int(ensure_float(summary.get("total_findings", 0))),
            "critical_findings": int(ensure_float(summary.get("critical_findings", 0))),
            "notes": ensure_list(summary.get("notes")),
        },
        "findings": ensure_list(payload.get("findings")),
        "strengths": ensure_list(payload.get("strengths")),
        "review_comment_markdown": payload.get("review_comment_markdown", ""),
    }
