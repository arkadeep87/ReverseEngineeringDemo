from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Iterator, TypedDict

from langgraph.graph import END, START, StateGraph

from agents import collate, forward_engineering, gap, requirements, reverse_legacy, reverse_target, technical_spec


PENDING_SME_APPROVAL = "PENDING_SME_APPROVAL"
SME_APPROVED = "SME_APPROVED"
SME_REJECTED = "SME_REJECTED"
PENDING_ARCHITECT_APPROVAL = "PENDING_ARCHITECT_APPROVAL"
ARCHITECT_APPROVED = "ARCHITECT_APPROVED"
ARCHITECT_REJECTED = "ARCHITECT_REJECTED"


class AppState(TypedDict, total=False):
    legacy_code_folder: str
    legacy_sql_folder: str
    target_code_folder: str
    target_sql_folder: str
    legacy_code_reverse_spec: dict
    legacy_sql_reverse_spec: dict
    target_code_reverse_spec: dict
    target_sql_reverse_spec: dict
    legacy_spec: dict
    target_spec: dict
    collated_spec: dict
    gap_analysis: dict
    requirements_draft: dict
    approved_requirements: dict
    technical_spec_draft: dict
    approved_technical_spec: dict
    forward_engineering_output: dict
    logs: list[dict]
    error: str


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_log(state: AppState, agent: str, message: str) -> None:
    state.setdefault("logs", []).append({"timestamp": _timestamp(), "agent": agent, "message": message})


def _approval_status(document: dict | None) -> str:
    if not isinstance(document, dict):
        return ""
    approval = document.get("approval", {})
    if not isinstance(approval, dict):
        return ""
    status = approval.get("status", "")
    return status if isinstance(status, str) else ""


def _resolve_approved_requirements(state: AppState) -> dict | None:
    approved = state.get("approved_requirements")
    if _approval_status(approved) == SME_APPROVED:
        return approved
    draft = state.get("requirements_draft")
    if _approval_status(draft) == SME_APPROVED:
        return draft
    return None


def _resolve_approved_technical_spec(state: AppState) -> dict | None:
    approved = state.get("approved_technical_spec")
    if _approval_status(approved) == ARCHITECT_APPROVED:
        return approved
    draft = state.get("technical_spec_draft")
    if _approval_status(draft) == ARCHITECT_APPROVED:
        return draft
    return None


def _requirements_gate_reason(state: AppState) -> str:
    status = _approval_status(state.get("approved_requirements"))
    if not status:
        status = _approval_status(state.get("requirements_draft"))
    if status == SME_APPROVED:
        return ""
    if status == SME_REJECTED:
        return "SME approval rejected"
    return "SME approval pending"


def _technical_spec_gate_reason(state: AppState) -> str:
    status = _approval_status(state.get("approved_technical_spec"))
    if not status:
        status = _approval_status(state.get("technical_spec_draft"))
    if status == ARCHITECT_APPROVED:
        return ""
    if status == ARCHITECT_REJECTED:
        return "Architect approval rejected"
    return "Architect approval pending"


def legacy_node(state: AppState) -> AppState:
    if state.get("legacy_code_reverse_spec") and state.get("legacy_sql_reverse_spec"):
        append_log(state, "reverse_legacy", "Legacy reverse engineering reused from current session state.")
        return {
            "legacy_code_reverse_spec": state["legacy_code_reverse_spec"],
            "legacy_sql_reverse_spec": state["legacy_sql_reverse_spec"],
            "logs": state["logs"],
        }
    code_result = reverse_legacy.run(state["legacy_code_folder"], "code", lambda a, m: append_log(state, a, m))
    sql_result = reverse_legacy.run(state["legacy_sql_folder"], "sql", lambda a, m: append_log(state, a, m))
    return {"legacy_code_reverse_spec": code_result, "legacy_sql_reverse_spec": sql_result, "logs": state["logs"]}


def legacy_collate_node(state: AppState) -> AppState:
    if state.get("legacy_spec"):
        append_log(state, "collate_legacy", "Legacy collated specification reused from current session state.")
        return {"legacy_spec": state["legacy_spec"], "logs": state["logs"]}
    result = collate.run(
        "Legacy Insurance System",
        state["legacy_code_reverse_spec"],
        state["legacy_sql_reverse_spec"],
        lambda _a, m: append_log(state, "collate_legacy", m),
    )
    return {"legacy_spec": result, "logs": state["logs"]}


def target_node(state: AppState) -> AppState:
    if state.get("target_code_reverse_spec") and state.get("target_sql_reverse_spec"):
        append_log(state, "reverse_target", "Target reverse engineering reused from current session state.")
        return {
            "target_code_reverse_spec": state["target_code_reverse_spec"],
            "target_sql_reverse_spec": state["target_sql_reverse_spec"],
            "logs": state["logs"],
        }
    code_result = reverse_target.run(state["target_code_folder"], "code", lambda a, m: append_log(state, a, m))
    sql_result = reverse_target.run(state["target_sql_folder"], "sql", lambda a, m: append_log(state, a, m))
    return {"target_code_reverse_spec": code_result, "target_sql_reverse_spec": sql_result, "logs": state["logs"]}


def target_collate_node(state: AppState) -> AppState:
    if state.get("target_spec") and state.get("collated_spec"):
        append_log(state, "collate_target", "Target collated specification reused from current session state.")
        return {
            "target_spec": state["target_spec"],
            "collated_spec": state["collated_spec"],
            "logs": state["logs"],
        }
    result = collate.run(
        "Target Insurance System",
        state["target_code_reverse_spec"],
        state["target_sql_reverse_spec"],
        lambda _a, m: append_log(state, "collate_target", m),
    )
    return {
        "target_spec": result,
        "collated_spec": build_comparison_overview(state.get("legacy_spec", {}), result),
        "logs": state["logs"],
    }


def gap_node(state: AppState) -> AppState:
    if state.get("gap_analysis"):
        append_log(state, "gap", "Gap analysis reused from current session state.")
        return {"gap_analysis": state["gap_analysis"], "logs": state["logs"]}
    result = gap.run(
        state["legacy_spec"],
        state["target_spec"],
        state["legacy_code_reverse_spec"],
        state["legacy_sql_reverse_spec"],
        state["target_code_reverse_spec"],
        state["target_sql_reverse_spec"],
        lambda a, m: append_log(state, a, m),
    )
    return {"gap_analysis": result, "logs": state["logs"]}


def requirements_node(state: AppState) -> AppState:
    if state.get("requirements_draft"):
        append_log(state, "requirements", "Requirements draft reused from current session state.")
        return {"requirements_draft": state["requirements_draft"], "logs": state["logs"]}
    result = requirements.run(state)
    return {"requirements_draft": result["requirements_draft"], "logs": state["logs"]}


def technical_spec_node(state: AppState) -> AppState:
    approved_requirements = _resolve_approved_requirements(state)
    if not approved_requirements:
        append_log(state, "technical_spec", f"Technical Specification skipped → {_requirements_gate_reason(state)}")
        return {"logs": state["logs"]}

    state["approved_requirements"] = approved_requirements
    result = technical_spec.run(state)
    return {
        "approved_requirements": approved_requirements,
        "technical_spec_draft": result["technical_spec_draft"],
        "logs": state["logs"],
    }


def forward_engineering_node(state: AppState) -> AppState:
    approved_requirements = _resolve_approved_requirements(state)
    if not approved_requirements:
        append_log(state, "forward_engineering", f"Forward Engineering skipped → {_requirements_gate_reason(state)}")
        return {"logs": state["logs"]}

    approved_technical_spec = _resolve_approved_technical_spec(state)
    if not approved_technical_spec:
        append_log(state, "forward_engineering", f"Forward Engineering skipped → {_technical_spec_gate_reason(state)}")
        return {"approved_requirements": approved_requirements, "logs": state["logs"]}

    result = forward_engineering.run(
        approved_requirements,
        approved_technical_spec,
        lambda a, m: append_log(state, a, m),
    )
    return {
        "approved_requirements": approved_requirements,
        "approved_technical_spec": approved_technical_spec,
        "forward_engineering_output": result,
        "logs": state["logs"],
    }


def build_comparison_overview(legacy_spec: dict, target_spec: dict) -> dict:
    shared_domains: list[str] = []
    if legacy_spec.get("fields") and target_spec.get("fields"):
        shared_domains.append("quote data capture")
    if legacy_spec.get("validations") and target_spec.get("validations"):
        shared_domains.append("eligibility and validation")
    if legacy_spec.get("calculations") and target_spec.get("calculations"):
        shared_domains.append("pricing and risk processing")

    key_differences = []
    if legacy_spec.get("country_specific_rules") and not target_spec.get("country_specific_rules"):
        key_differences.append(
            {
                "category": "country_logic",
                "legacy_position": "Legacy specification contains country-specific rules.",
                "target_position": "Target specification does not contain equivalent country-specific logic.",
                "impact": "Regional and compliance parity is incomplete.",
            }
        )
    if len(legacy_spec.get("business_rules", [])) != len(target_spec.get("business_rules", [])):
        key_differences.append(
            {
                "category": "business_rules",
                "legacy_position": f"{len(legacy_spec.get('business_rules', []))} consolidated rules extracted.",
                "target_position": f"{len(target_spec.get('business_rules', []))} consolidated rules extracted.",
                "impact": "Rule coverage differs across systems.",
            }
        )

    modernization_focus_areas = [
        {"focus_area": "pricing parity", "rationale": "Validate calculation and sequencing consistency.", "priority": "high"},
        {"focus_area": "compliance parity", "rationale": "Reconcile consent, tax, and audit controls.", "priority": "high"},
    ]

    return {
        "shared_domains": shared_domains,
        "key_differences": key_differences,
        "modernization_focus_areas": modernization_focus_areas,
        "confidence": {"overview_confidence": 0.72},
        "legacy_flow_map": legacy_spec.get("flow_map", {}),
        "target_flow_map": target_spec.get("flow_map", {}),
    }


def build_graph():
    workflow = StateGraph(AppState)
    workflow.add_node("reverse_legacy", legacy_node)
    workflow.add_node("collate_legacy", legacy_collate_node)
    workflow.add_node("reverse_target", target_node)
    workflow.add_node("collate_target", target_collate_node)
    workflow.add_node("gap", gap_node)
    workflow.add_node("requirements", requirements_node)
    workflow.add_node("technical_spec", technical_spec_node)
    workflow.add_node("forward_engineering", forward_engineering_node)
    workflow.add_edge(START, "reverse_legacy")
    workflow.add_edge("reverse_legacy", "collate_legacy")
    workflow.add_edge("collate_legacy", "reverse_target")
    workflow.add_edge("reverse_target", "collate_target")
    workflow.add_edge("collate_target", "gap")
    workflow.add_edge("gap", "requirements")
    workflow.add_edge("requirements", "technical_spec")
    workflow.add_edge("technical_spec", "forward_engineering")
    workflow.add_edge("forward_engineering", END)
    return workflow.compile()


def _build_initial_state(
    legacy_code_folder: str,
    legacy_sql_folder: str,
    target_code_folder: str,
    target_sql_folder: str,
    approved_requirements: dict | None = None,
    approved_technical_spec: dict | None = None,
    prior_state: AppState | None = None,
) -> AppState:
    initial_state: AppState = deepcopy(prior_state) if prior_state else {}
    initial_state["legacy_code_folder"] = legacy_code_folder
    initial_state["legacy_sql_folder"] = legacy_sql_folder
    initial_state["target_code_folder"] = target_code_folder
    initial_state["target_sql_folder"] = target_sql_folder
    initial_state.setdefault("logs", [])
    if approved_requirements is not None:
        initial_state["approved_requirements"] = approved_requirements
    if approved_technical_spec is not None:
        initial_state["approved_technical_spec"] = approved_technical_spec
    return initial_state


def stream_workflow(
    legacy_code_folder: str,
    legacy_sql_folder: str,
    target_code_folder: str,
    target_sql_folder: str,
    approved_requirements: dict | None = None,
    approved_technical_spec: dict | None = None,
    prior_state: AppState | None = None,
) -> Iterator[AppState]:
    graph = build_graph()
    state = _build_initial_state(
        legacy_code_folder=legacy_code_folder,
        legacy_sql_folder=legacy_sql_folder,
        target_code_folder=target_code_folder,
        target_sql_folder=target_sql_folder,
        approved_requirements=approved_requirements,
        approved_technical_spec=approved_technical_spec,
        prior_state=prior_state,
    )
    yield deepcopy(state)

    for chunk in graph.stream(state):
        for _node_name, update in chunk.items():
            state.update(update)
        yield deepcopy(state)


def stream_resume_from_requirements_approval(
    prior_state: AppState | None,
    approved_requirements: dict,
) -> Iterator[AppState]:
    state: AppState = deepcopy(prior_state) if prior_state else {}
    state.setdefault("logs", [])
    state["approved_requirements"] = approved_requirements
    state["requirements_draft"] = approved_requirements
    state.pop("approved_technical_spec", None)
    state.pop("technical_spec_draft", None)
    state.pop("forward_engineering_output", None)
    yield deepcopy(state)

    technical_spec_update = technical_spec_node(state)
    state.update(technical_spec_update)
    yield deepcopy(state)

    forward_engineering_update = forward_engineering_node(state)
    state.update(forward_engineering_update)
    yield deepcopy(state)


def stream_resume_from_technical_spec_approval(
    prior_state: AppState | None,
    approved_requirements: dict,
    approved_technical_spec: dict,
) -> Iterator[AppState]:
    state: AppState = deepcopy(prior_state) if prior_state else {}
    state.setdefault("logs", [])
    state["approved_requirements"] = approved_requirements
    state["requirements_draft"] = approved_requirements
    state["approved_technical_spec"] = approved_technical_spec
    state["technical_spec_draft"] = approved_technical_spec
    state.pop("forward_engineering_output", None)
    yield deepcopy(state)

    forward_engineering_update = forward_engineering_node(state)
    state.update(forward_engineering_update)
    yield deepcopy(state)


def run_workflow(
    legacy_code_folder: str,
    legacy_sql_folder: str,
    target_code_folder: str,
    target_sql_folder: str,
    approved_requirements: dict | None = None,
    approved_technical_spec: dict | None = None,
    prior_state: AppState | None = None,
) -> AppState:
    final_state: AppState = {}
    for state in stream_workflow(
        legacy_code_folder=legacy_code_folder,
        legacy_sql_folder=legacy_sql_folder,
        target_code_folder=target_code_folder,
        target_sql_folder=target_sql_folder,
        approved_requirements=approved_requirements,
        approved_technical_spec=approved_technical_spec,
        prior_state=prior_state,
    ):
        final_state = state
    return final_state
