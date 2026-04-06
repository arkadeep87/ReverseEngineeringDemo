from __future__ import annotations

import json
from pathlib import Path

from config import settings
from utils.parser import ensure_list

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - runtime fallback
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover - runtime fallback
    Anthropic = None


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _render_prompt_template(prompt: str, prompt_args: dict[str, str]) -> str:
    rendered = prompt
    for key, value in prompt_args.items():
        rendered = rendered.replace(f"{{{key}}}", value)
    return rendered


def _slugify_identifier(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value.upper()).strip("_")
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned or "UNKNOWN"


def _extract_country_rule_context(legacy: dict, gap: dict) -> list[dict]:
    legacy_rules = ensure_list(legacy.get("country_specific_rules"))
    missing_features = ensure_list(gap.get("missing_features"))
    rule_comparison = ensure_list(gap.get("rule_comparison"))

    country_map: dict[str, list[str]] = {}

    for rule in legacy_rules:
        if not isinstance(rule, dict):
            continue
        country = str(rule.get("country", "")).strip()
        description = str(rule.get("description", "")).strip()
        rule_name = str(rule.get("rule_name", "")).strip()
        if not country:
            continue
        country_map.setdefault(country, [])
        for detail in (rule_name, description):
            if detail and detail not in country_map[country]:
                country_map[country].append(detail)

    for item in missing_features:
        if not isinstance(item, str):
            continue
        lowered = item.lower()
        for country in list(country_map.keys()):
            if country.lower() in lowered and item not in country_map[country]:
                country_map[country].append(item)

    for item in rule_comparison:
        if not isinstance(item, dict):
            continue
        description = str(item.get("description", "")).strip()
        evidence = ensure_list(item.get("evidence"))
        combined = " ".join([description, *[str(entry) for entry in evidence]]).lower()
        for country in list(country_map.keys()):
            if country.lower() in combined and description and description not in country_map[country]:
                country_map[country].append(description)

    results = []
    for country, details in sorted(country_map.items()):
        normalized_details = [detail for detail in details if detail]
        results.append(
            {
                "country": country,
                "requirement_id": f"FR-COUNTRY-{_slugify_identifier(country)}",
                "details": normalized_details,
            }
        )
    return results


def _build_mock_reverse_response(system_name: str, artifact_kind: str, file_names: list[str], is_legacy: bool) -> dict:
    is_code = artifact_kind == "code"
    return {
        "system_name": system_name,
        "artifact_kind": artifact_kind,
        "summary": f"Mock {artifact_kind} reverse-engineered spec for {system_name}.",
        "fields": [
            {
                "name": "customer_id" if is_code else "quote_id",
                "canonical_name": "customer_id" if is_code else "quote_id",
                "type": "string" if is_code else ("integer" if is_legacy else "uuid"),
                "required": True,
                "source_entity": "quote_form" if is_code else "quote",
                "source_layer": "ui" if is_code else "db",
                "business_meaning": "Key quote input captured or persisted through the quote flow.",
                "ui_metadata": {
                    "screen_name": "Quote Generation",
                    "number_of_fields": 8,
                    "control_type": "text",
                    "html_tag": "input" if not is_legacy and is_code else "",
                    "component_tag": "TextBox" if is_legacy and is_code else ("input" if is_code else ""),
                    "section": "customer",
                    "visible": bool(is_code),
                    "editable": bool(is_code),
                    "placeholder": "",
                }
                if is_code
                else {},
                "db_metadata": {}
                if is_code
                else {
                    "table_name": "quote_context" if is_legacy else "quotes",
                    "column_name": "quote_id",
                    "column_type": "INT" if is_legacy else "UUID",
                    "nullable": False,
                    "primary_key": True,
                    "foreign_key": False,
                    "default_value": None,
                    "indexed": True,
                    "derived_or_computed": False,
                },
                "source_reference": file_names,
            }
        ],
        "business_rules": [
            {
                "id": "BR-CODE-FLOW" if is_code else "BR-DB-FLOW",
                "rule_name": "Quote orchestration flow" if is_code else "Database pricing and persistence flow",
                "category": "workflow",
                "description": "Artifacts describe how the quote process is orchestrated across layers.",
                "trigger": "Generate Quote action",
                "condition": "Required inputs are supplied to the system.",
                "outcome": "Validation, pricing, and persistence steps execute in order.",
                "priority": "high",
                "source_reference": file_names,
                "confidence": 0.85,
            }
        ],
        "country_specific_rules": []
        if is_code
        else [
            {
                "country": "Spain" if not is_legacy else "Multi-country",
                "rule_name": "Country-aware pricing logic",
                "rule_type": "db_logic",
                "description": "Stored logic applies country-aware tax or adjustment behavior.",
                "impacted_products": ["health", "travel", "family"],
                "source_reference": file_names,
                "confidence": 0.82,
            }
        ],
        "validations": [
            {
                "validation_name": "Required input validation" if is_code else "Procedure-level eligibility validation",
                "field_or_entity": "quote_form" if is_code else "quote_context",
                "validation_type": "ui_validation" if is_code else "stored_procedure_validation",
                "rule": "Artifacts show validation gates before quote completion.",
                "error_behavior": "The flow rejects or stops invalid submissions.",
                "source_reference": file_names,
            }
        ],
        "calculations": [
            {
                "calculation_name": "Pricing handoff" if is_code else "Database pricing calculation",
                "category": "pricing",
                "formula_or_logic": "Artifacts describe the inputs and outputs of pricing logic.",
                "inputs": ["policy_type", "coverage_amount"],
                "outputs": ["final_premium"],
                "source_reference": file_names,
            }
        ],
        "ui_components": [
            {
                "component_name": "Quote Generation Form",
                "component_type": "form",
                "screen_or_route": "Quote Generation",
                "purpose": "Capture quote inputs and submit the quote request.",
                "actions": ["generate_quote"],
                "controls": [
                    {
                        "control_name": "txtCustomerId" if is_legacy else "customerId",
                        "control_type": "textbox" if is_legacy else "text_input",
                        "label": "Customer Id",
                        "bound_field": "customer_id",
                        "data_type": "string",
                        "required": True,
                        "default_value": "",
                        "visible": True,
                        "editable": True,
                        "options": [],
                        "events": ["change"],
                    },
                    {
                        "control_name": "cboPolicyType" if is_legacy else "policyType",
                        "control_type": "combobox" if is_legacy else "select",
                        "label": "Policy Type",
                        "bound_field": "policy_type",
                        "data_type": "string",
                        "required": True,
                        "default_value": "HEALTH",
                        "visible": True,
                        "editable": True,
                        "options": ["HEALTH", "TRAVEL", "FAMILY", "CORPORATE"],
                        "events": ["change"],
                    },
                    {
                        "control_name": "txtCoverage" if is_legacy else "coverageAmount",
                        "control_type": "textbox" if is_legacy else "number_input",
                        "label": "Coverage Amount",
                        "bound_field": "coverage_amount",
                        "data_type": "decimal",
                        "required": True,
                        "default_value": 50000,
                        "visible": True,
                        "editable": True,
                        "options": [],
                        "events": ["change"],
                    },
                ],
                "source_reference": file_names,
            }
        ]
        if is_code
        else [],
        "classes": [
            {
                "class_name": "CommonCountryQuoteProcessor" if is_legacy else "QuoteWorkflowService",
                "class_type": "service",
                "responsibility": "Coordinates validation, pricing, persistence, and audit processing.",
                "dependencies": ["validation_service", "pricing_service", "persistence_service"],
                "source_reference": file_names,
            }
        ]
        if is_code
        else [],
        "methods": [
            {
                "method_name": "OnGenerateQuote" if is_legacy else "generateQuote",
                "owner": "BaseQuoteGenerationForm" if is_legacy else "QuoteApiService",
                "visibility": "private" if is_legacy else "public",
                "returns": "void" if is_legacy else "Observable<QuoteResponse>",
                "parameters": [
                    {"name": "quote_request", "type": "QuoteRequest", "required": True, "description": "Canonical quote request payload."}
                ],
                "calls": ["workflow_service"],
                "source_reference": file_names,
            }
        ]
        if is_code
        else [],
        "procedures": []
        if is_code
        else [
            {
                "procedure_name": "sp_calculate_quote" if is_legacy else "fn_apply_spain_adjustment",
                "procedure_type": "stored_procedure" if is_legacy else "function",
                "parameters": [
                    {
                        "name": "quote_id" if is_legacy else "p_policy_type",
                        "direction": "input",
                        "type": "INT" if is_legacy else "text",
                        "required": True,
                        "default_value": None,
                        "description": "Primary procedure input.",
                    },
                    {
                        "name": "country_code" if is_legacy else "p_premium_amount",
                        "direction": "input",
                        "type": "VARCHAR(2)" if is_legacy else "numeric",
                        "required": True,
                        "default_value": None,
                        "description": "Country or pricing input used in logic branches.",
                    },
                ],
                "returns": ["final_premium"] if is_legacy else ["adjustment_amount"],
                "side_effects": ["pricing update", "table writes"],
                "logic_summary": "Calculates pricing-related outputs and applies procedural orchestration.",
                "source_reference": file_names,
            }
        ],
        "procedure_dependencies": [
            {
                "from": "submit_handler" if is_code else "pricing_orchestration",
                "to": "workflow_service" if is_code else "tax_discount_risk_logic",
                "dependency_type": "method_call" if is_code else "procedure_call",
                "source_reference": file_names,
            }
        ],
        "table_dependencies": []
        if is_code
        else [
            {
                "table_name": "quote_context" if is_legacy else "quotes",
                "role": "transactional persistence",
                "operation": "update" if is_legacy else "insert",
                "columns": ["quote_id", "final_premium", "tax_amount"],
                "dependent_procedures": ["sp_calculate_quote"] if is_legacy else ["quote.repository"],
                "source_reference": file_names,
            }
        ],
        "api_endpoints": []
        if is_legacy or not is_code
        else [
            {
                "method": "POST",
                "path": "/api/v1/quotes/generate",
                "request_fields": ["customer_id", "policy_type", "coverage_amount", "country_code"],
                "response_fields": ["quote_id", "pricing.final_premium"],
                "purpose": "Generate quote",
                "source_reference": file_names,
            }
        ],
        "confidence": {
            "overall": 0.84,
            "evidence_quality": "mock_demo",
            "inferred_items": ["dependency chain", "canonical field intent"],
            "assumptions": ["Generated from local mock mode because no live LLM call was available."],
        },
        "source_files": file_names,
        "notes": [f"Mock {artifact_kind} reverse output with {'code' if is_code else 'SQL'}-specific emphasis."],
    }


def _build_mock_collate_response(system_name: str, code_reverse_spec: dict, sql_reverse_spec: dict) -> dict:
    source_files = list(dict.fromkeys(code_reverse_spec.get("source_files", []) + sql_reverse_spec.get("source_files", [])))
    return {
        "system_name": system_name,
        "summary": f"Consolidated business transaction specification for {system_name} built from separate code and SQL reverse engineering passes.",
        "fields": code_reverse_spec.get("fields", []) + sql_reverse_spec.get("fields", []),
        "business_rules": code_reverse_spec.get("business_rules", []) + sql_reverse_spec.get("business_rules", []),
        "country_specific_rules": sql_reverse_spec.get("country_specific_rules", []),
        "validations": code_reverse_spec.get("validations", []) + sql_reverse_spec.get("validations", []),
        "calculations": code_reverse_spec.get("calculations", []) + sql_reverse_spec.get("calculations", []),
        "confidence": {"collation_confidence": 0.86, "synthesis_quality": "mock_demo", "notes": ["Mock collation output."]},
        "source_files": source_files,
        "notes": code_reverse_spec.get("notes", []) + sql_reverse_spec.get("notes", []),
        "transaction_flow": [
            {"stage": "code_reverse_engineering", "description": "Application source was reverse engineered first.", "source_reference": code_reverse_spec.get("source_files", [])},
            {"stage": "sql_reverse_engineering", "description": "Database source was reverse engineered separately.", "source_reference": sql_reverse_spec.get("source_files", [])},
            {"stage": "canonical_collation", "description": "Both reverse outputs were merged into a unified business flow.", "source_reference": source_files},
        ],
        "entities": [
            {"entity_name": "Quote", "entity_type": "transactional", "description": "Primary insurance quotation record."},
            {"entity_name": "Customer", "entity_type": "master", "description": "Customer profile used during validation and pricing."},
        ],
        "integrations": code_reverse_spec.get("api_endpoints", []),
        "persistence_model": sql_reverse_spec.get("table_dependencies", []),
        "audit_controls": [{"control_name": "Quote audit trail", "description": "Events are recorded during quote generation and compliance handling."}],
        "exception_paths": [{"exception_name": "Validation failure", "description": "Processing stops when validation or compliance checks fail."}],
        "flow_map": {
            "nodes": [
                {"id": "code_reverse", "label": "Code Reverse", "type": "analysis"},
                {"id": "sql_reverse", "label": "SQL Reverse", "type": "analysis"},
                {"id": "collate", "label": "Canonical Collate", "type": "synthesis"},
                {"id": "validate", "label": "Validation", "type": "process"},
                {"id": "price", "label": "Pricing", "type": "process"},
                {"id": "persist", "label": "Persistence", "type": "process"},
            ],
            "edges": [
                {"from": "code_reverse", "to": "collate", "label": "ui/classes/apis"},
                {"from": "sql_reverse", "to": "collate", "label": "sp/tables/logic"},
                {"from": "collate", "to": "validate", "label": "canonical model"},
                {"from": "validate", "to": "price", "label": "approved"},
                {"from": "price", "to": "persist", "label": "final premium"},
            ],
            "diagram_text": "Code Reverse -> Canonical Collate <- SQL Reverse -> Validation -> Pricing -> Persistence",
        },
        "source_breakdown": {
            "code_source_files": code_reverse_spec.get("source_files", []),
            "sql_source_files": sql_reverse_spec.get("source_files", []),
        },
    }


def _build_mock_requirements_response(input_payload: dict) -> dict:
    legacy = input_payload.get("legacy", {})
    target = input_payload.get("target", {})
    gap = input_payload.get("gap", {})
    screen_name = "Quote Generation"
    legacy_name = legacy.get("system_name", "Legacy Insurance System")
    target_name = target.get("system_name", "Target Insurance System")
    missing_features = ensure_list(gap.get("missing_features"))
    compliance_gaps = ensure_list(gap.get("compliance_gaps"))
    open_questions = ensure_list(gap.get("compliance_gaps"))[:3]
    country_rule_context = _extract_country_rule_context(legacy, gap)

    functional_requirements = [
        {
            "id": "FR-001",
            "title": "Preserve quote generation workflow parity",
            "description": "The target solution must preserve the end-to-end validation, pricing, and persistence workflow supported by the legacy system.",
            "priority": "High",
            "rationale": "Core quote generation capability must remain functionally consistent during modernization.",
            "source_gap": "Missing or partial workflow parity in gap analysis.",
            "acceptance_criteria": [
                "Quote request is validated before pricing.",
                "Pricing results are persisted only after successful validation.",
                "Errors are surfaced when validation fails.",
            ],
        }
    ]

    if missing_features:
        functional_requirements.append(
            {
                "id": "FR-002",
                "title": "Build missing legacy capabilities into the target solution",
                "description": "All business capabilities identified as missing in the current target must be implemented in the modernized target solution.",
                "priority": "High",
                "rationale": "The modernization scope should close legacy-to-target capability gaps rather than preserve the current limited target scope.",
                "source_gap": "; ".join(missing_features),
                "acceptance_criteria": [
                    "Each missing legacy capability identified in the gap analysis is represented in the delivered target solution.",
                    "Country-specific rules missing from the current target are implemented where required for parity.",
                    "SME review confirms that no approved legacy capability has been omitted from the future-state requirements.",
                ],
            }
        )

    for country_rule in country_rule_context:
        country = country_rule["country"]
        country_requirement_id = country_rule["requirement_id"]
        detail_summary = "; ".join(country_rule["details"]) or f"Missing {country} quote-processing rules identified in the legacy-to-target gap."
        functional_requirements.append(
            {
                "id": country_requirement_id,
                "title": f"Implement {country} quote-generation rules",
                "description": f"The target solution must implement the {country}-specific quote-generation behavior that exists in the legacy system but is missing or incomplete in the current target, including the identified validations, pricing or tax handling, reference-data usage, workflow branching, and user-facing behavior required for {country}.",
                "priority": "High",
                "rationale": f"{country}-specific business rules are part of the approved modernization scope and must be implemented explicitly rather than treated as generic regional logic.",
                "source_gap": detail_summary,
                "acceptance_criteria": [
                    f"{country} quote requests apply the approved {country}-specific validations, pricing or tax logic, and workflow behavior defined by the legacy baseline and gap analysis.",
                    f"The target solution uses the required {country} reference data, calculations, and rule outcomes consistently across UI, API, and persistence processing where applicable.",
                    f"Business and test evidence can trace {country_requirement_id} from requirement through design, implementation, and country-specific scenario validation.",
                ],
            }
        )

    return {
        "document_type": "requirements_draft",
        "screen_name": screen_name,
        "business_context": f"Draft modernization requirements bridging {legacy_name} to {target_name}, assuming missing legacy capabilities and controls must be built into the future-state target solution.",
        "functional_requirements": functional_requirements,
        "non_functional_requirements": [
            {
                "id": "NFR-001",
                "title": "Auditability",
                "description": "The target implementation should preserve operational traceability for quote processing.",
                "priority": "High",
            }
        ],
        "compliance_requirements": [
            {
                "id": "CR-001",
                "title": "Consent and regulatory controls",
                "description": "The modernized flow must preserve consent and regional compliance controls called out in the gap analysis.",
                "region": "EU",
                "priority": "High",
            }
        ],
        "data_requirements": [
            {
                "id": "DR-001",
                "entity": "Quote",
                "requirement": "Quote data must maintain canonical field parity between legacy and target systems.",
            }
        ],
        "ui_requirements": [
            {
                "id": "UIR-001",
                "field_or_component": screen_name,
                "requirement": "The UI must capture the required inputs needed for validation and pricing.",
            }
        ],
        "api_requirements": [
            {
                "id": "APIR-001",
                "api_name": "Quote Generation API",
                "requirement": "APIs must support the approved quote-generation workflow and traceability expectations.",
            }
        ],
        "migration_requirements": [
            {
                "id": "MR-001",
                "requirement": "Country-specific rules and compliance-sensitive logic missing from the current target must be implemented for migration parity before release.",
            }
        ],
        "assumptions": ["Draft generated from collated legacy/target specs and gap analysis context."],
        "open_questions_for_sme": open_questions,
        "review_notes": ["This is a draft pending SME validation."],
        "approval": {
            "status": "PENDING_SME_APPROVAL",
            "required_reviewer_role": "SME",
            "approved_by": "",
            "approved_on": "",
            "review_comments": "",
        },
    }


def _build_mock_technical_spec_response(input_payload: dict) -> dict:
    requirements = input_payload.get("requirements", {})
    functional_requirements = ensure_list(requirements.get("functional_requirements"))
    country_requirement_ids = [
        str(item.get("id", ""))
        for item in functional_requirements
        if isinstance(item, dict) and str(item.get("id", "")).startswith("FR-COUNTRY")
    ]

    ui_design = [
        {
            "component": "QuoteGenerationComponent",
            "responsibility": "Capture quote inputs and submit approved quote-generation requests.",
            "related_requirement_ids": ["FR-001"],
        }
    ]
    service_design = [
        {
            "service_name": "QuoteWorkflowService",
            "responsibility": "Coordinate validation, pricing, compliance, and persistence.",
            "business_rules_supported": ["Validation before pricing", "Persist after successful validation"],
            "related_requirement_ids": ["FR-001", "CR-001"],
        }
    ]
    rule_configuration_design = [
        {
            "rule_area": "Country-specific pricing and compliance",
            "approach": "Externalize regional rules and validation thresholds where possible.",
            "details": "Support configuration-backed regional processing for modernization parity.",
            "related_requirement_ids": ["MR-001", "CR-001"],
        }
    ]
    validation_design = [
        {
            "validation_name": "Quote request validation",
            "logic": "Validate required fields and compliance preconditions before pricing execution.",
            "layer": "API",
            "related_requirement_ids": ["FR-001", "CR-001"],
        }
    ]
    integration_design = [
        {
            "integration_point": "Reference and pricing data sources",
            "details": "Use repository-backed integrations for pricing, compliance, and persistence flows.",
        }
    ]

    if country_requirement_ids:
        ui_design.append(
            {
                "component": "Country-aware quote generation workflow",
                "responsibility": "Support country-sensitive quote behavior, inputs, messages, and scenario handling where required by approved requirements.",
                "related_requirement_ids": country_requirement_ids,
            }
        )
        service_design.append(
            {
                "service_name": "CountryRuleOrchestrationService",
                "responsibility": "Apply country-specific quote rules, adjustments, and validations based on approved business requirements.",
                "business_rules_supported": ["Country-specific rule selection", "Country-specific pricing adjustments", "Country-specific validation handling"],
                "related_requirement_ids": [*country_requirement_ids, "MR-001"],
            }
        )
        rule_configuration_design.append(
            {
                "rule_area": "Country-specific quote logic",
                "approach": "Implement explicit country-aware rule handling with traceable configuration or service logic.",
                "details": "Support country-specific rules that are missing from the current target and required for parity with the approved modernization scope.",
                "related_requirement_ids": country_requirement_ids,
            }
        )
        validation_design.append(
            {
                "validation_name": "Country-specific validation handling",
                "logic": "Apply country-sensitive validation and compliance checks where required by approved business requirements.",
                "layer": "API",
                "related_requirement_ids": country_requirement_ids,
            }
        )
        integration_design.append(
            {
                "integration_point": "Country rule and reference data support",
                "details": "Support country-specific pricing, tax, and reference-data lookups required by approved country-specific requirements.",
            }
        )

    return {
        "document_type": "technical_spec_draft",
        "screen_name": "Quote Generation",
        "target_stack": {"frontend": "Angular", "backend": "Node.js", "database": "PostgreSQL"},
        "ui_design": ui_design,
        "api_design": [
            {
                "name": "GenerateQuote",
                "method": "POST",
                "path": "/api/v1/quotes/generate",
                "request_fields": ["customer_id", "policy_type", "coverage_amount", "country_code"],
                "response_fields": ["quote_id", "final_premium"],
                "related_requirement_ids": ["FR-001", "APIR-001"],
            }
        ],
        "service_design": service_design,
        "data_design": [
            {
                "entity": "Quote",
                "fields": ["quote_id", "customer_id", "policy_type", "coverage_amount", "final_premium"],
                "relationships": ["Quote belongs to Customer"],
                "related_requirement_ids": ["DR-001"],
            }
        ],
        "rule_configuration_design": rule_configuration_design,
        "validation_design": validation_design,
        "security_and_compliance_design": [
            {
                "area": "Consent and audit",
                "design_decision": "Enforce compliance checks before persistence and log key workflow events.",
                "related_requirement_ids": ["CR-001", "NFR-001"],
            }
        ],
        "integration_design": integration_design,
        "assumptions": ["Draft generated from approved requirements."],
        "open_questions_for_architect": [],
        "review_notes": ["This is a draft pending architect validation."],
        "approval": {
            "status": "PENDING_ARCHITECT_APPROVAL",
            "required_reviewer_role": "Architect",
            "approved_by": "",
            "approved_on": "",
            "review_comments": "",
        },
    }


def _build_mock_forward_engineering_response(input_payload: dict) -> dict:
    requirements = input_payload.get("requirements", {})
    functional_requirements = ensure_list(requirements.get("functional_requirements"))
    country_requirement_ids = [
        str(item.get("id", ""))
        for item in functional_requirements
        if isinstance(item, dict) and str(item.get("id", "")).startswith("FR-COUNTRY")
    ]

    angular_files = [
        {
            "file_name": "quote-generation.component.ts",
            "purpose": "Implements the approved quote-generation UI flow.",
            "related_requirement_ids": ["FR-001"],
            "content": "// Mock Angular implementation artifact",
        }
    ]
    nodejs_files = [
        {
            "file_name": "quote-workflow.service.js",
            "purpose": "Implements the approved orchestration flow.",
            "related_requirement_ids": ["FR-001", "CR-001"],
            "content": "// Mock Node.js implementation artifact",
        }
    ]
    postgres_files = [
        {
            "file_name": "quote_workflow.sql",
            "purpose": "Supports approved persistence and rule behavior.",
            "related_requirement_ids": ["DR-001"],
            "content": "-- Mock PostgreSQL implementation artifact",
        }
    ]
    test_cases = [
        {
            "id": "TC-001",
            "title": "Validate quote generation happy path",
            "related_requirement_ids": ["FR-001"],
            "type": "Integration",
            "scenario": "Submit a valid quote request and verify validation, pricing, and persistence complete successfully.",
        }
    ]
    traceability_summary = ["FR-001 traced across UI, API, and persistence artifacts."]

    if country_requirement_ids:
        nodejs_files.append(
            {
                "file_name": "country-rule-orchestration.service.js",
                "purpose": "Implements country-specific rule handling required by approved modernization scope.",
                "related_requirement_ids": [*country_requirement_ids, "MR-001"],
                "content": "// Mock Node.js country-specific implementation artifact",
            }
        )
        postgres_files.append(
            {
                "file_name": "country_rule_configuration.sql",
                "purpose": "Supports country-specific rule configuration and persistence needs.",
                "related_requirement_ids": country_requirement_ids,
                "content": "-- Mock PostgreSQL country-specific implementation artifact",
            }
        )
        test_cases.append(
            {
                "id": "TC-COUNTRY-001",
                "title": "Validate country-specific quote behavior",
                "related_requirement_ids": country_requirement_ids,
                "type": "Integration",
                "scenario": "Execute approved country-specific quote scenarios and confirm country-aware logic, pricing, and validation outcomes are implemented.",
            }
        )
        traceability_summary.append(f"{', '.join(country_requirement_ids)} traced across country-aware service logic, configuration support, and integration tests.")

    return {
        "document_type": "forward_engineering_output",
        "angular_files": angular_files,
        "nodejs_files": nodejs_files,
        "postgres_files": postgres_files,
        "test_cases": test_cases,
        "generation_notes": ["Generated from approved requirements and approved technical specification."],
        "traceability_summary": traceability_summary,
    }


def _build_mock_validation_response(input_payload: dict) -> dict:
    generated_files = ensure_list(input_payload.get("generated_files"))
    impacted_files = [item.get("generated_relative_path") or item.get("file_name", "") for item in generated_files[:3] if isinstance(item, dict)]
    differences = [
        {
            "title": "Country-specific parity is only partially implemented",
            "category": "business_rules",
            "severity": "high",
            "source_expectation": "Generated target should preserve approved source parity for country-sensitive quote behavior.",
            "generated_behavior": "Generated artifacts focus on the core quote flow, but broader country-specific handling is not fully evidenced.",
            "impacted_files": impacted_files,
            "recommendation": "Extend workflow, pricing, and persistence files to cover approved country-specific scenarios.",
        },
        {
            "title": "Generated artifact coverage is narrower than the full source estate",
            "category": "coverage",
            "severity": "medium",
            "source_expectation": "Generated target should cover the approved source and technical design scope.",
            "generated_behavior": "Only a subset of files is generated and validated as modified.",
            "impacted_files": impacted_files,
            "recommendation": "Review uncovered source behaviors and add follow-on generated changes where required.",
        },
    ]
    suggestions = [
        {
            "priority": "high",
            "suggestion": "Validate each generated service against approved functional requirements and legacy rule coverage.",
            "target_files": impacted_files,
            "rationale": "Service-layer mismatches create the biggest parity risk.",
        },
        {
            "priority": "medium",
            "suggestion": "Add targeted regression tests for source behaviors that are not clearly represented in the generated output.",
            "target_files": impacted_files,
            "rationale": "This reduces the chance of source-to-generated behavior drift.",
        },
    ]
    return {
        "summary": {
            "overall_status": "partially_aligned",
            "sync_score": 0.74,
            "difference_count": len(differences),
            "suggestion_count": len(suggestions),
            "notes": ["Mock validation compares generated artifacts to source intent and approved design at a high level."],
        },
        "differences": differences,
        "suggestions": suggestions,
        "confidence": {
            "validation_confidence": 0.82,
            "notes": ["Mock validation output generated without live LLM execution."],
        },
    }


def _build_mock_response(agent_name: str, input_payload: dict) -> dict:
    system_name = input_payload.get("system_name", agent_name)
    file_names = [item.get("name", "unknown") for item in input_payload.get("files", [])]
    artifact_kind = input_payload.get("artifact_kind", "")

    if agent_name in {"reverse_legacy", "reverse_target"}:
        return _build_mock_reverse_response(system_name, artifact_kind, file_names, is_legacy=agent_name == "reverse_legacy")

    if agent_name == "collate":
        return _build_mock_collate_response(
            input_payload.get("system_name", "Insurance System"),
            input_payload.get("code_reverse_spec", {}),
            input_payload.get("sql_reverse_spec", {}),
        )

    if agent_name == "requirements":
        return _build_mock_requirements_response(input_payload)

    if agent_name == "technical_spec":
        return _build_mock_technical_spec_response(input_payload)

    if agent_name == "forward_engineering":
        return _build_mock_forward_engineering_response(input_payload)

    if agent_name == "validation":
        return _build_mock_validation_response(input_payload)

    return {
        "missing_features": [
            "Germany, France, and Italy policy tax handling is absent in target inputs.",
            "GDPR consent enforcement is not present in the target system.",
        ],
        "incorrect_implementations": [
            "Target validation model does not appear to block policy persistence when privacy consent is missing."
        ],
        "compliance_gaps": [
            "EU privacy consent workflow is missing.",
            "Country-specific insurance taxation controls are incomplete.",
        ],
        "risks": [
            {
                "risk_name": "GDPR non-compliance",
                "category": "regulatory",
                "severity": "High",
                "description": "Missing EU consent enforcement may allow unauthorized processing.",
                "impacted_area": "quote processing",
                "likely_outcome": "Potential fines and compliance breaches.",
                "mitigation_hint": "Implement consent validation and auditable enforcement.",
            },
            {
                "risk_name": "Regional pricing mismatch",
                "category": "financial",
                "severity": "High",
                "description": "Country-specific tax logic is absent from the target flow.",
                "impacted_area": "premium calculation",
                "likely_outcome": "Incorrect premiums and reconciliation issues.",
                "mitigation_hint": "Introduce tax reference data and targeted pricing tests.",
            },
        ],
        "rule_comparison": [
            {
                "rule_id": "BR-GDPR",
                "rule_name": "GDPR Consent Rule",
                "category": "compliance",
                "legacy_status": "Present",
                "target_status": "Missing",
                "gap_type": "compliance_gap",
                "risk_level": "High",
                "description": "Legacy blocks EU processing without consent while target lacks equivalent enforcement.",
                "evidence": ["sp_validate_gdpr_consent.sybase.sql", "quote.validation.js"],
                "recommended_action": "Add consent validation and persistence checks in the target flow.",
                "confidence": 0.95,
            },
            {
                "rule_id": "BR-EU-TAX",
                "rule_name": "EU Tax Logic",
                "category": "tax",
                "legacy_status": "Present",
                "target_status": "Missing",
                "gap_type": "missing_feature",
                "risk_level": "High",
                "description": "Legacy includes country-specific tax calculation and reference data not found in target.",
                "evidence": ["country_tax_rules.sybase.sql", "sp_lookup_country_tax.sybase.sql"],
                "recommended_action": "Port country-specific tax rules and reference tables.",
                "confidence": 0.9,
            },
            {
                "rule_id": "BR-AGE-RISK",
                "rule_name": "Age Risk Loading",
                "category": "risk",
                "legacy_status": "Present",
                "target_status": "Partial",
                "gap_type": "incorrect_implementation",
                "risk_level": "Medium",
                "description": "Both systems apply age-related risk factors but thresholds and loadings differ.",
                "evidence": ["sp_apply_risk_loading.sybase.sql", "rating.service.js"],
                "recommended_action": "Compare thresholds and factor increments line by line.",
                "confidence": 0.76,
            },
        ],
        "common_rules_missed": [
            {
                "rule_id": "BR-AGE-RISK",
                "rule_name": "Age Risk Loading",
                "legacy_formula_or_logic": "Apply incremental risk loading when driver age crosses defined threshold bands used by legacy pricing procedures.",
                "target_formula_or_logic": "Target applies a simplified risk adjustment and does not preserve the same threshold bands or loading increments.",
                "gap_summary": "The shared risk-loading rule is only partially implemented in target.",
                "business_impact": "Premium outcomes may differ across the standard quote journey, creating pricing leakage and inconsistent underwriting outcomes.",
                "evidence": ["sp_apply_risk_loading.sybase.sql", "rating.service.js"],
                "recommended_action": "Implement the approved common risk-loading thresholds and factors in target pricing services.",
            }
        ],
        "country_specific_rules_missed": [
            {
                "country": "Germany",
                "rule_id": "BR-DE-TAX",
                "rule_name": "Germany Insurance Tax Logic",
                "legacy_formula_or_logic": "Apply Germany-specific insurance tax calculation using legacy country tax lookup and premium adjustment rules before final premium confirmation.",
                "target_formula_or_logic": "No equivalent Germany-specific tax logic is present in the target flow.",
                "gap_summary": "Germany-specific tax calculation is missing in target.",
                "business_impact": "German quotes may produce incorrect premium totals and downstream reconciliation issues.",
                "evidence": ["country_tax_rules.sybase.sql", "sp_lookup_country_tax.sybase.sql"],
                "recommended_action": "Implement Germany tax rule lookup, calculation, and traceable test coverage in the target solution.",
            },
            {
                "country": "Italy",
                "rule_id": "BR-IT-TAX",
                "rule_name": "Italy Insurance Tax Logic",
                "legacy_formula_or_logic": "Apply Italy-specific premium tax handling and related reference-data lookup before persistence.",
                "target_formula_or_logic": "No equivalent Italy-specific tax or reference-data handling is present in the target flow.",
                "gap_summary": "Italy-specific tax and reference-data behavior is missing in target.",
                "business_impact": "Italian quote outcomes may be inaccurate and non-compliant with expected regional processing.",
                "evidence": ["country_tax_rules.sybase.sql", "sp_lookup_country_tax.sybase.sql"],
                "recommended_action": "Implement Italy-specific tax logic and supporting reference-data integration in the target solution.",
            },
        ],
        "confidence": {
            "gap_confidence": 0.87,
            "coverage_of_analysis": {
                "pricing": "covered",
                "compliance": "covered",
                "country_logic": "covered",
                "auditability": "partial",
            },
            "notes": ["Mock gap analysis generated without live LLM execution."],
        },
    }


def call_llm_json(agent_name: str, prompt: str, input_payload: dict, require_live_call: bool = False) -> dict:
    prompt_args = {"payload": json.dumps(input_payload, ensure_ascii=False, indent=2)}
    for key, value in input_payload.items():
        prompt_args[key] = json.dumps(value, ensure_ascii=False, indent=2)
    formatted_prompt = _render_prompt_template(prompt, prompt_args)

    if settings.model.startswith("claude"):
        if not settings.anthropic_api_key or Anthropic is None:
            if require_live_call:
                raise RuntimeError(
                    "Caching is disabled, so a live Anthropic call is required. "
                    "Set ANTHROPIC_API_KEY and ensure the anthropic package is installed."
                )
            return _build_mock_response(agent_name, input_payload)

        client = Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=settings.model,
            max_tokens=4000,
            system="Return strict JSON only. Do not use markdown fences.",
            messages=[{"role": "user", "content": formatted_prompt}],
        )
        text_parts = [block.text for block in response.content if getattr(block, "type", "") == "text"]
        return {"raw_text": "\n".join(text_parts)}

    if not settings.openai_api_key or OpenAI is None:
        if require_live_call:
            raise RuntimeError(
                "Caching is disabled, so a live OpenAI call is required. "
                "Set OPENAI_API_KEY and ensure the openai package is installed."
            )
        return _build_mock_response(agent_name, input_payload)

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.model,
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": "Return strict JSON only. Do not use markdown fences."}]},
            {"role": "user", "content": [{"type": "input_text", "text": formatted_prompt}]},
        ],
    )
    return {"raw_text": response.output_text}
