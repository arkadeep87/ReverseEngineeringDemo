from __future__ import annotations

from datetime import datetime
import difflib
import json
from pathlib import Path
import shutil
from typing import Any

import pandas as pd
import streamlit as st

from config import settings
from graph import (
    ARCHITECT_APPROVED,
    ARCHITECT_REJECTED,
    PENDING_ARCHITECT_APPROVAL,
    PENDING_SME_APPROVAL,
    SME_APPROVED,
    SME_REJECTED,
    run_workflow,
    stream_workflow,
)
from utils.cache import AgentCache


st.set_page_config(
    page_title="AI Enabled App Migration Platform",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_OPTIONS = [
    "gpt-5.4-mini",
    "gpt-5.4",
    "gpt-5-mini",
    "gpt-5",
    "gpt-4o-mini",
    "claude-sonnet-4-20250514",
    "claude-opus-4-1-20250805",
]

WORKFLOW_PHASES = [
    ("reverse_legacy", "Analyzing legacy VB and SQL files"),
    ("collate_legacy", "Collating legacy business flow"),
    ("reverse_target", "Analyzing target code and SQL files"),
    ("collate_target", "Collating target business flow"),
    ("gap", "Analyzing requirement gaps between legacy and target system"),
    ("requirements", "Drafting incremental business requirements"),
    ("technical_spec", "Drafting incremental technical specification"),
    ("forward_engineering", "Generating forward-engineered code components"),
]


def apply_enterprise_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(11, 78, 140, 0.14), transparent 28%),
                linear-gradient(180deg, #f4f7fb 0%, #edf2f7 100%);
        }
        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #16263d 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        [data-testid="stSidebar"] * {
            color: #e5eef8;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] label {
            color: #e5eef8;
        }
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea,
        [data-testid="stSidebar"] [data-baseweb="input"] input {
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            background-color: #ffffff !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="select"] span,
        [data-testid="stSidebar"] [data-baseweb="popover"] *,
        [data-testid="stSidebar"] [data-baseweb="base-input"],
        [data-testid="stSidebar"] [role="combobox"],
        [data-testid="stSidebar"] [role="listbox"],
        [data-testid="stSidebar"] [role="option"] {
            background-color: #ffffff !important;
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
        }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] .stText,
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stToggle label {
            color: #e5eef8 !important;
        }
        .hero-card, .panel-card, .metric-card, .gap-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            box-shadow: 0 18px 38px rgba(15, 23, 42, 0.08);
        }
        .hero-card {
            padding: 1.5rem 1.75rem;
            min-height: 180px;
        }
        .panel-card {
            padding: 1.1rem 1.2rem;
        }
        .phase-card {
            height: 206px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .phase-title {
            min-height: 82px;
            display: flex;
            align-items: flex-start;
        }
        .metric-card {
            padding: 1rem 1.1rem;
        }
        .gap-card {
            padding: 1rem 1.15rem;
            height: 100%;
        }
        .eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.72rem;
            color: #0b4e8c;
            font-weight: 700;
        }
        .hero-title {
            font-size: 2.15rem;
            line-height: 1.05;
            margin: 0.35rem 0 0.55rem 0;
            color: #10233b;
            font-weight: 800;
        }
        .hero-copy, .muted-copy {
            color: #4b5d73;
            font-size: 0.98rem;
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #10233b;
            margin-bottom: 0.65rem;
        }
        .status-chip {
            display: inline-block;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            background: transparent;
            color: #0b4e8c;
            font-size: 0.8rem;
            font-weight: 700;
            margin-right: 0.4rem;
            margin-bottom: 0.4rem;
        }
        .risk-high {
            border-left: 5px solid #c62828;
        }
        .risk-medium {
            border-left: 5px solid #ef6c00;
        }
        .risk-low {
            border-left: 5px solid #2e7d32;
        }
        .small-label {
            font-size: 0.78rem;
            color: #6b7c93;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.3rem;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #10233b;
            margin: 0;
        }
        .metric-subtle {
            color: #61758b;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, subtle: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="small-label">{label}</div>
            <p class="metric-value">{value}</p>
            <div class="metric-subtle">{subtle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def to_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def render_bullets(items: list, empty_message: str) -> None:
    if items:
        for item in items:
            st.write(f"- {item}")
    else:
        st.write(empty_message)


def normalize_for_table(items: Any) -> pd.DataFrame:
    if isinstance(items, list):
        if not items:
            return pd.DataFrame()
        if all(isinstance(item, dict) for item in items):
            return pd.json_normalize(items, sep=".")
        return pd.DataFrame({"value": [str(item) for item in items]})
    if isinstance(items, dict):
        return pd.json_normalize(items, sep=".")
    if items in (None, ""):
        return pd.DataFrame()
    return pd.DataFrame({"value": [str(items)]})


def sanitize_dataframe_for_display(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe

    def normalize_cell(value: Any) -> Any:
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        return value

    return dataframe.map(normalize_cell)


def build_nested_rows(items: list[dict], nested_key: str, parent_keys: list[str], child_prefix: str = "") -> list[dict]:
    rows: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        nested_items = item.get(nested_key, [])
        if not isinstance(nested_items, list):
            continue
        for nested_item in nested_items:
            row = {key: item.get(key) for key in parent_keys}
            if isinstance(nested_item, dict):
                for key, value in nested_item.items():
                    row[f"{child_prefix}{key}" if child_prefix else key] = value
            else:
                row[f"{child_prefix}value" if child_prefix else "value"] = nested_item
            rows.append(row)
    return rows


def render_table(items: Any, empty_message: str = "No data available.") -> None:
    dataframe = normalize_for_table(items)
    if dataframe.empty:
        st.info(empty_message)
        return
    dataframe = sanitize_dataframe_for_display(dataframe)
    st.dataframe(dataframe, use_container_width=True, hide_index=True)


def render_notes(items: list[Any]) -> None:
    if not items:
        st.info("No notes available.")
        return
    for item in items:
        st.markdown(
            f"""
            <div class="panel-card" style="margin-bottom: 0.7rem;">
                <div>{item}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def create_run_trace_dir() -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = settings.outputs_dir / "runs" / timestamp
    suffix = 1
    while run_dir.exists():
        suffix += 1
        run_dir = settings.outputs_dir / "runs" / f"{timestamp}_{suffix}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_json_trace(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_run_trace_snapshot(run_dir: Path, state: dict, status: str) -> None:
    logs = state.get("logs", [])
    write_json_trace(run_dir / "workflow_log.json", {"status": status, "logs": logs})
    write_json_trace(run_dir / "latest_state.json", {"status": status, "state": state})


def finalize_run_trace(run_dir: Path, state: dict) -> None:
    write_run_trace_snapshot(run_dir, state, "completed")
    write_json_trace(run_dir / "final_state.json", state)


def write_error_trace(run_dir: Path, error_message: str, state: dict) -> None:
    write_run_trace_snapshot(run_dir, state, "failed")
    write_json_trace(
        run_dir / "error.json",
        {
            "error": error_message,
            "logs": state.get("logs", []),
            "state": state,
        },
    )


def render_live_execution_status(log_placeholder, logs: list[dict]) -> None:
    with log_placeholder.container():
        st.markdown("**Live Execution Status**")
        if not logs:
            st.info("Waiting for the first workflow update...")
            return
        recent_logs = logs[-8:]
        for entry in recent_logs:
            st.markdown(
                f"- `{entry.get('agent', 'system')}`: {entry.get('message', '')}"
            )


def deep_copy_document(document: dict | None) -> dict:
    if not isinstance(document, dict):
        return {}
    return json.loads(json.dumps(document))


def get_approval_status(document: dict | None, default_status: str) -> str:
    if not isinstance(document, dict):
        return default_status
    approval = document.get("approval", {})
    if not isinstance(approval, dict):
        return default_status
    status = approval.get("status", default_status)
    return status if isinstance(status, str) and status else default_status


def update_document_approval(document: dict | None, status: str, comments: str, reviewer_label: str) -> dict:
    updated = deep_copy_document(document)
    updated.setdefault("approval", {})
    updated["approval"]["status"] = status
    updated["approval"]["required_reviewer_role"] = reviewer_label
    updated["approval"]["approved_by"] = reviewer_label if "APPROVED" in status else ""
    updated["approval"]["approved_on"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    updated["approval"]["review_comments"] = comments
    return updated


def init_approval_state() -> None:
    st.session_state.setdefault("approved_requirements", None)
    st.session_state.setdefault("approved_technical_spec", None)
    st.session_state.setdefault("sme_comments", "")
    st.session_state.setdefault("architect_comments", "")
    st.session_state.setdefault("auto_run_analysis", False)


def sync_approval_state_from_result(result: dict) -> None:
    requirements_draft = result.get("requirements_draft", {})
    technical_spec_draft = result.get("technical_spec_draft", {})

    approved_requirements = st.session_state.get("approved_requirements")
    if approved_requirements is None and get_approval_status(requirements_draft, PENDING_SME_APPROVAL) == SME_APPROVED:
        st.session_state["approved_requirements"] = deep_copy_document(requirements_draft)

    approved_technical_spec = st.session_state.get("approved_technical_spec")
    if approved_technical_spec is None and get_approval_status(technical_spec_draft, PENDING_ARCHITECT_APPROVAL) == ARCHITECT_APPROVED:
        st.session_state["approved_technical_spec"] = deep_copy_document(technical_spec_draft)


def render_approval_summary(label: str, status: str, comments: str) -> None:
    st.markdown(f"**{label} Status:** `{status}`")
    if comments.strip():
        st.caption(f"Review comments: {comments.strip()}")


def filter_country_specific_requirements(functional_requirements: list[dict]) -> list[dict]:
    return [
        item
        for item in functional_requirements
        if isinstance(item, dict) and str(item.get("id", "")).startswith("FR-COUNTRY")
    ]


def filter_country_specific_technical_design(technical_spec_draft: dict) -> dict[str, list[dict]]:
    country_requirement_ids = {
        str(item.get("id", ""))
        for item in filter_country_specific_requirements(technical_spec_draft.get("source_requirements", []))
        if isinstance(item, dict)
    }
    if not country_requirement_ids:
        for section_name in (
            "ui_design",
            "api_design",
            "service_design",
            "data_design",
            "rule_configuration_design",
            "validation_design",
            "security_and_compliance_design",
        ):
            for item in technical_spec_draft.get(section_name, []):
                if not isinstance(item, dict):
                    continue
                related = item.get("related_requirement_ids", [])
                if isinstance(related, list):
                    for requirement_id in related:
                        requirement_id_text = str(requirement_id)
                        if requirement_id_text.startswith("FR-COUNTRY"):
                            country_requirement_ids.add(requirement_id_text)

    def _filter(section_name: str) -> list[dict]:
        results: list[dict] = []
        for item in technical_spec_draft.get(section_name, []):
            if not isinstance(item, dict):
                continue
            related = item.get("related_requirement_ids", [])
            if isinstance(related, list) and any(str(req_id) in country_requirement_ids for req_id in related):
                results.append(item)
        return results

    return {
        "ui_design": _filter("ui_design"),
        "api_design": _filter("api_design"),
        "service_design": _filter("service_design"),
        "data_design": _filter("data_design"),
        "rule_configuration_design": _filter("rule_configuration_design"),
        "validation_design": _filter("validation_design"),
        "security_and_compliance_design": _filter("security_and_compliance_design"),
    }


def render_requirements_document(requirements_draft: dict) -> None:
    if not requirements_draft:
        st.info("Requirements draft will appear after analysis runs.")
        return

    st.markdown("**Overview**")
    st.write(requirements_draft.get("business_context", "No business context available."))

    top1, top2, top3 = st.columns(3)
    top1.metric("Functional", len(requirements_draft.get("functional_requirements", [])))
    top2.metric("Open SME Questions", len(requirements_draft.get("open_questions_for_sme", [])))
    top3.metric("Compliance", len(requirements_draft.get("compliance_requirements", [])))
    summary_tab, functional_tab, supporting_tab, approval_tab = st.tabs(
        ["Summary", "Functional Requirements", "Supporting Requirements", "Approval"]
    )

    with summary_tab:
        st.markdown("**Screen Name**")
        st.write(requirements_draft.get("screen_name", ""))
        st.markdown("**Assumptions**")
        render_table(requirements_draft.get("assumptions", []), "No assumptions recorded.")
        st.markdown("**Open Questions For SME**")
        render_table(requirements_draft.get("open_questions_for_sme", []), "No open questions recorded.")
        st.markdown("**Review Notes**")
        render_table(requirements_draft.get("review_notes", []), "No review notes recorded.")

    with functional_tab:
        render_table(requirements_draft.get("functional_requirements", []), "No functional requirements generated.")

    with supporting_tab:
        st.markdown("**Non-Functional Requirements**")
        render_table(requirements_draft.get("non_functional_requirements", []), "No non-functional requirements generated.")
        st.markdown("**Compliance Requirements**")
        render_table(requirements_draft.get("compliance_requirements", []), "No compliance requirements generated.")
        st.markdown("**Data Requirements**")
        render_table(requirements_draft.get("data_requirements", []), "No data requirements generated.")
        st.markdown("**UI Requirements**")
        render_table(requirements_draft.get("ui_requirements", []), "No UI requirements generated.")
        st.markdown("**API Requirements**")
        render_table(requirements_draft.get("api_requirements", []), "No API requirements generated.")
        st.markdown("**Migration Requirements**")
        render_table(requirements_draft.get("migration_requirements", []), "No migration requirements generated.")

    with approval_tab:
        render_table(requirements_draft.get("approval", {}), "No approval metadata available.")


def render_technical_spec_document(technical_spec_draft: dict) -> None:
    if not technical_spec_draft:
        st.info("Technical specification draft will appear after SME approval and the next analysis run.")
        return

    st.markdown("**Overview**")
    st.write(f"Target stack: {json.dumps(technical_spec_draft.get('target_stack', {}), ensure_ascii=False)}")

    top1, top2, top3 = st.columns(3)
    top1.metric("UI Design", len(technical_spec_draft.get("ui_design", [])))
    top2.metric("API Design", len(technical_spec_draft.get("api_design", [])))
    top3.metric("Architect Questions", len(technical_spec_draft.get("open_questions_for_architect", [])))

    summary_tab, design_tab, review_tab = st.tabs(["Summary", "Design Details", "Approval"])

    with summary_tab:
        st.markdown("**Screen Name**")
        st.write(technical_spec_draft.get("screen_name", ""))
        st.markdown("**Target Stack**")
        render_table(technical_spec_draft.get("target_stack", {}), "No stack details available.")
        st.markdown("**Assumptions**")
        render_table(technical_spec_draft.get("assumptions", []), "No assumptions recorded.")
        st.markdown("**Open Questions For Architect**")
        render_table(technical_spec_draft.get("open_questions_for_architect", []), "No architect questions recorded.")
        st.markdown("**Review Notes**")
        render_table(technical_spec_draft.get("review_notes", []), "No review notes recorded.")

    with design_tab:
        st.markdown("**UI Design**")
        render_table(technical_spec_draft.get("ui_design", []), "No UI design generated.")
        st.markdown("**API Design**")
        render_table(technical_spec_draft.get("api_design", []), "No API design generated.")
        st.markdown("**Service Design**")
        render_table(technical_spec_draft.get("service_design", []), "No service design generated.")
        st.markdown("**Data Design**")
        render_table(technical_spec_draft.get("data_design", []), "No data design generated.")
        st.markdown("**Rule Configuration Design**")
        render_table(technical_spec_draft.get("rule_configuration_design", []), "No rule configuration design generated.")
        st.markdown("**Validation Design**")
        render_table(technical_spec_draft.get("validation_design", []), "No validation design generated.")
        st.markdown("**Security And Compliance Design**")
        render_table(
            technical_spec_draft.get("security_and_compliance_design", []),
            "No security and compliance design generated.",
        )
        st.markdown("**Integration Design**")
        render_table(technical_spec_draft.get("integration_design", []), "No integration design generated.")

    with review_tab:
        render_table(technical_spec_draft.get("approval", {}), "No approval metadata available.")


def render_forward_engineering_document(output: dict) -> None:
    if not output:
        st.info("Forward engineering output will appear after architect approval and the next analysis run.")
        return

    top1, top2, top3, top4 = st.columns(4)
    top1.metric("Angular Files", len(output.get("angular_files", [])))
    top2.metric("Node.js Files", len(output.get("nodejs_files", [])))
    top3.metric("PostgreSQL Files", len(output.get("postgres_files", [])))
    top4.metric("Test Cases", len(output.get("test_cases", [])))

    files_tab, tests_tab, notes_tab = st.tabs(["Generated Files", "Test Cases", "Notes"])

    with files_tab:
        st.markdown("**Angular Files**")
        render_table(output.get("angular_files", []), "No Angular files generated.")
        st.markdown("**Node.js Files**")
        render_table(output.get("nodejs_files", []), "No Node.js files generated.")
        st.markdown("**PostgreSQL Files**")
        render_table(output.get("postgres_files", []), "No PostgreSQL files generated.")

    with tests_tab:
        render_table(output.get("test_cases", []), "No test cases generated.")

    with notes_tab:
        st.markdown("**Generation Notes**")
        render_table(output.get("generation_notes", []), "No generation notes available.")
        st.markdown("**Traceability Summary**")
        render_table(output.get("traceability_summary", []), "No traceability summary available.")


def get_generated_target_root() -> Path:
    return settings.outputs_dir / "forward_engineering" / "target_candidate"


def build_generated_artifact_path(group_name: str, file_name: str) -> Path:
    root = get_generated_target_root()
    safe_name = Path(file_name).name
    if group_name == "angular_files":
        return root / "frontend" / "src" / "app" / "quote-generation" / safe_name
    if group_name == "nodejs_files":
        return root / "backend" / "src" / safe_name
    return root / "sql" / safe_name


def materialize_forward_engineering_output(output: dict) -> dict:
    cache = AgentCache(settings.cache_dir)
    if settings.cache_enabled:
        cached = cache.load("forward_engineering_ui", output)
        if cached:
            generated_root = Path(cached.get("generated_root", ""))
            generated_files = cached.get("generated_files", [])
            if generated_root.exists() and all(Path(item.get("generated_path", "")).exists() for item in generated_files):
                return cached

    generated_root = get_generated_target_root()
    if generated_root.exists():
        shutil.rmtree(generated_root)
    generated_root.mkdir(parents=True, exist_ok=True)

    generated_files: list[dict] = []
    for group_name in ("angular_files", "nodejs_files", "postgres_files"):
        for item in output.get(group_name, []):
            file_name = item.get("file_name", "")
            if not file_name:
                continue
            destination = build_generated_artifact_path(group_name, file_name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(item.get("content", ""), encoding="utf-8")
            generated_files.append(
                {
                    "group": group_name,
                    "file_name": file_name,
                    "generated_path": str(destination),
                    "purpose": item.get("purpose", ""),
                    "related_requirement_ids": item.get("related_requirement_ids", []),
                    "content": item.get("content", ""),
                }
            )

    materialized = {"generated_root": str(generated_root), "generated_files": generated_files}
    if settings.cache_enabled:
        cache.save("forward_engineering_ui", output, materialized)
    return materialized


def find_matching_target_file(file_name: str, search_roots: list[str]) -> Path | None:
    for root in search_roots:
        root_path = Path(root)
        if not root_path.exists():
            continue
        direct_path = root_path / file_name
        if direct_path.exists():
            return direct_path
        matches = list(root_path.rglob(file_name))
        if matches:
            return matches[0]
    return None


def build_forward_engineering_comparison(generated_files: list[dict], target_code_folder: str, target_sql_folder: str) -> list[dict]:
    search_roots = [target_code_folder, target_sql_folder]
    comparisons: list[dict] = []

    for item in generated_files:
        file_name = item.get("file_name", "")
        generated_content = item.get("content", "")
        original_path = find_matching_target_file(file_name, search_roots)
        original_content = original_path.read_text(encoding="utf-8") if original_path else ""
        if not original_path:
            status = "Added"
        elif original_content == generated_content:
            status = "Unchanged"
        else:
            status = "Modified"

        diff_text = "\n".join(
            difflib.unified_diff(
                original_content.splitlines(),
                generated_content.splitlines(),
                fromfile=f"original/{file_name}",
                tofile=f"generated/{file_name}",
                lineterm="",
            )
        )

        comparisons.append(
            {
                **item,
                "status": status,
                "original_path": str(original_path) if original_path else "",
                "original_content": original_content,
                "diff_text": diff_text,
            }
        )

    return comparisons


def render_forward_engineering_summary(output: dict, comparison_items: list[dict], generated_root: str) -> None:
    if not output:
        st.info("Forward engineering output will appear after architect approval and the next analysis run.")
        return

    added_count = sum(1 for item in comparison_items if item.get("status") == "Added")
    modified_count = sum(1 for item in comparison_items if item.get("status") == "Modified")
    unchanged_count = sum(1 for item in comparison_items if item.get("status") == "Unchanged")

    top1, top2, top3, top4 = st.columns(4)
    top1.metric("Added Files", added_count)
    top2.metric("Modified Files", modified_count)
    top3.metric("Unchanged Files", unchanged_count)
    top4.metric("Total Generated", str(len(comparison_items)))

    st.caption(f"Generated target candidate path: {generated_root}")

    summary_tab, files_tab, tests_tab, notes_tab = st.tabs(["Change Summary", "Generated Files", "Test Cases", "Notes"])

    with summary_tab:
        summary_rows = [
            {
                "status": item.get("status", ""),
                "file_name": item.get("file_name", ""),
                "purpose": item.get("purpose", ""),
                "generated_path": item.get("generated_path", ""),
                "original_path": item.get("original_path", ""),
            }
            for item in comparison_items
        ]
        render_table(summary_rows, "No generated files available.")

    with files_tab:
        st.markdown("**Angular Files**")
        render_table(output.get("angular_files", []), "No Angular files generated.")
        st.markdown("**Node.js Files**")
        render_table(output.get("nodejs_files", []), "No Node.js files generated.")
        st.markdown("**PostgreSQL Files**")
        render_table(output.get("postgres_files", []), "No PostgreSQL files generated.")

    with tests_tab:
        render_table(output.get("test_cases", []), "No test cases generated.")

    with notes_tab:
        st.markdown("**Generation Notes**")
        render_table(output.get("generation_notes", []), "No generation notes available.")
        st.markdown("**Traceability Summary**")
        render_table(output.get("traceability_summary", []), "No traceability summary available.")


def render_forward_engineering_proof(comparison_items: list[dict]) -> None:
    if not comparison_items:
        st.info("Forward engineering proof will appear after forward engineering generates files.")
        return

    file_options = [item.get("file_name", f"generated_{index}") for index, item in enumerate(comparison_items, start=1)]
    selected_file = st.selectbox("Generated artifact", options=file_options, key="forward_proof_file")
    selected_artifact = next((item for item in comparison_items if item.get("file_name") == selected_file), {})

    generated_content = selected_artifact.get("content", "")
    original_path_value = selected_artifact.get("original_path", "")
    original_path = Path(original_path_value) if original_path_value else None
    original_content = selected_artifact.get("original_content", "")

    original_tab, generated_tab, diff_tab = st.tabs(["Original", "Generated", "Diff"])
    with original_tab:
        if original_path:
            st.caption(f"Matched target file: {original_path}")
            st.code(original_content, language="text")
        else:
            st.info("No matching target file found for this generated artifact.")

    with generated_tab:
        st.code(generated_content, language="text")

    with diff_tab:
        if original_path:
            diff_text = selected_artifact.get("diff_text", "")
            st.code(diff_text or "No differences detected.", language="diff")
        else:
            st.info("Diff is unavailable because no original target file match was found.")


def render_phase_progress(logs: list[dict]) -> None:
    phase_map = dict(WORKFLOW_PHASES)
    seen = {entry.get("agent") for entry in logs}
    completed = sum(1 for key, _label in WORKFLOW_PHASES if key in seen)
    progress = completed / len(WORKFLOW_PHASES)
    st.progress(progress, text=f"Workflow completion: {int(progress * 100)}%")

    cols = st.columns(len(phase_map))
    for index, (agent, label) in enumerate(phase_map.items()):
        state = "Complete" if agent in seen else "Pending"
        cols[index].markdown(
            f"""
            <div class="panel-card phase-card">
                <div class="small-label">Phase {index + 1}</div>
                <div class="phase-title">
                    <div class="section-title">{label}</div>
                </div>
                <span class="status-chip">{state}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_spec(spec: dict, title: str) -> None:
    st.subheader(title)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.write(spec.get("summary", "No summary available."))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fields", len(spec.get("fields", [])))
    col2.metric("Common Rules", len(spec.get("business_rules", [])))
    col3.metric("Validations", len(spec.get("validations", [])))
    col4.metric("Calculations", len(spec.get("calculations", [])))
    st.markdown("</div>", unsafe_allow_html=True)

    (
        summary_tab,
        fields_tab,
        rules_tab,
        country_tab,
        validations_tab,
        calculations_tab,
        structure_tab,
        notes_tab,
    ) = st.tabs(
        ["Summary", "Fields", "Common Rules", "Country-Specific Rules", "Validations", "Calculations", "Structure", "Notes"]
    )

    with summary_tab:
        st.markdown("**System Summary**")
        st.write(spec.get("summary", "No summary available."))
        st.markdown("**Confidence**")
        render_table(spec.get("confidence", {}), "No confidence metadata available.")
        st.markdown("**Source Files**")
        render_table(spec.get("source_files", []), "No source files recorded.")

    with fields_tab:
        render_table(spec.get("fields", []), "No fields extracted.")

    with rules_tab:
        render_table(spec.get("business_rules", []), "No common rules extracted.")

    with country_tab:
        render_table(spec.get("country_specific_rules", []), "No country-specific rules extracted.")

    with validations_tab:
        render_table(spec.get("validations", []), "No validations extracted.")

    with calculations_tab:
        render_table(spec.get("calculations", []), "No calculations extracted.")

    with structure_tab:
        st.markdown("**UI Components**")
        render_table(spec.get("ui_components", []), "No UI components extracted.")
        ui_control_rows = build_nested_rows(
            spec.get("ui_components", []),
            "controls",
            ["component_name", "component_type", "screen_or_route"],
            child_prefix="control_",
        )
        st.markdown("**UI Controls**")
        render_table(ui_control_rows, "No UI controls extracted.")
        st.markdown("**Classes**")
        render_table(spec.get("classes", []), "No classes extracted.")
        st.markdown("**Methods**")
        render_table(spec.get("methods", []), "No methods extracted.")
        method_parameter_rows = build_nested_rows(spec.get("methods", []), "parameters", ["owner", "method_name"], child_prefix="param_")
        st.markdown("**Method Parameters**")
        render_table(method_parameter_rows, "No method parameters extracted.")
        st.markdown("**Procedures**")
        render_table(spec.get("procedures", []), "No procedures extracted.")
        procedure_parameter_rows = build_nested_rows(
            spec.get("procedures", []),
            "parameters",
            ["procedure_name", "procedure_type"],
            child_prefix="param_",
        )
        st.markdown("**Procedure Parameters**")
        render_table(procedure_parameter_rows, "No procedure parameters extracted.")
        st.markdown("**Procedure Dependencies**")
        render_table(spec.get("procedure_dependencies", []), "No procedure dependencies extracted.")
        st.markdown("**Table Dependencies**")
        render_table(spec.get("table_dependencies", []), "No table dependencies extracted.")
        st.markdown("**API Endpoints**")
        render_table(spec.get("api_endpoints", []), "No API endpoints extracted.")
        if spec.get("source_breakdown"):
            st.markdown("**Source Breakdown**")
            render_table(spec.get("source_breakdown", {}), "No source breakdown available.")

    with notes_tab:
        render_notes(spec.get("notes", []))
        errors = spec.get("read_errors", [])
        if errors:
            st.warning("File read warnings")
            render_bullets(errors, "No file warnings.")


def render_gap(gap_analysis: dict) -> None:
    confidence = to_float(gap_analysis.get("confidence", {}).get("gap_confidence", 0.0))
    missing_features = gap_analysis.get("missing_features", [])
    incorrect_implementations = gap_analysis.get("incorrect_implementations", [])
    compliance_gaps = gap_analysis.get("compliance_gaps", [])
    risks = gap_analysis.get("risks", [])
    common_rules_missed = gap_analysis.get("common_rules_missed", [])
    country_specific_rules_missed = gap_analysis.get("country_specific_rules_missed", [])

    top1, top2, top3, top4 = st.columns(4)
    with top1:
        render_metric_card("Gap Confidence", f"{confidence:.0%}", "Model-estimated certainty")
    with top2:
        render_metric_card("Missing Features", str(len(missing_features)), "Expected legacy behavior absent")
    with top3:
        render_metric_card("Compliance Gaps", str(len(compliance_gaps)), "Privacy and regulatory gaps")
    with top4:
        render_metric_card("Implementation Issues", str(len(incorrect_implementations)), "Potential parity defects")

    summary_tab, missed_rules_tab, comparison_tab, confidence_tab = st.tabs(["Gap Summary", "Rules Missed", "Rule Comparison", "Confidence"])

    with summary_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="gap-card risk-medium">', unsafe_allow_html=True)
            st.markdown("**Missing Features**")
            render_bullets(missing_features, "No missing features detected.")
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="gap-card risk-high">', unsafe_allow_html=True)
            st.markdown("**Compliance Gaps**")
            render_bullets(compliance_gaps, "No compliance gaps detected.")
            st.markdown("</div>", unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="gap-card risk-medium">', unsafe_allow_html=True)
            st.markdown("**Incorrect Implementations**")
            render_bullets(incorrect_implementations, "No incorrect implementations detected.")
            st.markdown("</div>", unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="gap-card risk-high">', unsafe_allow_html=True)
            st.markdown("**Risks**")
            if risks and all(isinstance(item, dict) for item in risks):
                render_table(risks, "No risks detected.")
            else:
                render_bullets(risks, "No risks detected.")
            st.markdown("</div>", unsafe_allow_html=True)

    with missed_rules_tab:
        common_tab, country_tab = st.tabs(["Common Rules Missed", "Country-Specific Rules Missed"])
        with common_tab:
            render_table(common_rules_missed, "No common rules missed were identified.")
        with country_tab:
            render_table(country_specific_rules_missed, "No country-specific rules missed were identified.")

    with comparison_tab:
        comparison_df = normalize_for_table(gap_analysis.get("rule_comparison", []))
        if not comparison_df.empty and "confidence" in comparison_df.columns:
            comparison_df["confidence"] = comparison_df["confidence"].map(
                lambda value: f"{to_float(value):.0%}" if value not in (None, "") else value
            )
        if comparison_df.empty:
            st.info("No rule comparison data available.")
        else:
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    with confidence_tab:
        render_table(gap_analysis.get("confidence", {}), "No confidence data available.")


def render_logs(logs: list[dict]) -> None:
    if not logs:
        st.info("No execution logs yet.")
        return

    log_df = pd.DataFrame(logs)
    if "timestamp" in log_df.columns:
        log_df["timestamp"] = pd.to_datetime(log_df["timestamp"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

    st.markdown("**Execution Timeline**")
    for entry in logs:
        ts = entry.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%H:%M:%S")
        except ValueError:
            pass
        st.markdown(
            f"""
            <div class="panel-card" style="margin-bottom: 0.7rem;">
                <div class="small-label">{ts} | {entry.get("agent", "system")}</div>
                <div>{entry.get("message", "")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Structured Log Table", expanded=False):
        st.dataframe(log_df, use_container_width=True, hide_index=True)


def render_flow_map(flow_map: dict, title: str) -> None:
    st.subheader(title)
    if not flow_map:
        st.info("No flow map available.")
        return

    nodes = flow_map.get("nodes", [])
    edges = flow_map.get("edges", [])
    if not nodes or not edges:
        st.info("No flow map nodes or edges available.")
        return

    dot_lines = [
        "digraph G {",
        'graph [rankdir=LR, pad="0.6", nodesep="0.7", ranksep="1.1", bgcolor="transparent"];',
        'node [shape=box, style="rounded,filled", fillcolor="#eef4fb", color="#6f94bf", fontname="Helvetica", fontsize="16", margin="0.25,0.18", penwidth="1.4"];',
        'edge [color="#4f6f96", fontname="Helvetica", fontsize="13", penwidth="1.2"];',
    ]
    for node in nodes:
        dot_lines.append(f'"{node.get("id", "")}" [label="{node.get("label", "")}"];')
    for edge in edges:
        dot_lines.append(f'"{edge.get("from", "")}" -> "{edge.get("to", "")}" [label="{edge.get("label", "")}"];')
    dot_lines.append("}")
    dot_graph = "\n".join(dot_lines)

    try:
        st.graphviz_chart(dot_graph, use_container_width=True)
    except Exception:
        st.code(dot_graph, language="dot")

    if flow_map.get("diagram_text"):
        st.caption(flow_map["diagram_text"])

    linear_flow = " -> ".join(node.get("label", "") for node in nodes if node.get("label"))
    if linear_flow:
        st.markdown("**Linear View**")
        st.code(linear_flow, language="text")

    node_tab, edge_tab = st.tabs(["Flow Nodes", "Flow Edges"])
    with node_tab:
        render_table(nodes, "No flow nodes available.")
    with edge_tab:
        render_table(edges, "No flow edges available.")


def render_step_outputs(result: dict) -> None:
    (
        legacy_code_reverse_step,
        legacy_sql_reverse_step,
        legacy_collate_step,
        target_code_reverse_step,
        target_sql_reverse_step,
        target_collate_step,
        gap_step,
    ) = st.tabs(
        [
            "Step 1: Legacy Code Reverse",
            "Step 2: Legacy SQL Reverse",
            "Step 3: Legacy Collate",
            "Step 4: Target Code Reverse",
            "Step 5: Target SQL Reverse",
            "Step 6: Target Collate",
            "Step 7: Gap Analysis",
        ]
    )

    with legacy_code_reverse_step:
        render_spec(result.get("legacy_code_reverse_spec", {}), "Legacy Source Code Reverse Engineering Output")

    with legacy_sql_reverse_step:
        render_spec(result.get("legacy_sql_reverse_spec", {}), "Legacy SQL Reverse Engineering Output")

    with legacy_collate_step:
        render_spec(result.get("legacy_spec", {}), "Legacy Consolidated Specification")
        render_flow_map(result.get("legacy_spec", {}).get("flow_map", {}), "Legacy Flow Map")

    with target_code_reverse_step:
        render_spec(result.get("target_code_reverse_spec", {}), "Target Source Code Reverse Engineering Output")

    with target_sql_reverse_step:
        render_spec(result.get("target_sql_reverse_spec", {}), "Target SQL Reverse Engineering Output")

    with target_collate_step:
        render_spec(result.get("target_spec", {}), "Target Consolidated Specification")
        render_flow_map(result.get("target_spec", {}).get("flow_map", {}), "Target Flow Map")

    with gap_step:
        render_gap(result.get("gap_analysis", {}))


def render_comparison(collated: dict, gap_analysis: dict) -> None:
    domains_tab, differences_tab, focus_tab, common_rules_tab, country_rules_tab, rules_tab = st.tabs(
        ["Shared Domains", "Key Differences", "Focus Areas", "Common Rules Missed", "Country Rules Missed", "Rule Comparison"]
    )

    with domains_tab:
        render_table(collated.get("shared_domains", []), "No shared domains available.")

    with differences_tab:
        render_table(collated.get("key_differences", []), "No key differences available.")

    with focus_tab:
        render_table(collated.get("modernization_focus_areas", []), "No focus areas available.")

    with common_rules_tab:
        render_table(gap_analysis.get("common_rules_missed", []), "No common rules missed available.")

    with country_rules_tab:
        render_table(gap_analysis.get("country_specific_rules_missed", []), "No country-specific rules missed available.")

    with rules_tab:
        render_table(gap_analysis.get("rule_comparison", []), "No rule comparison available.")


def main() -> None:
    apply_enterprise_theme()
    init_approval_state()
    st.title("AI Powered Migration Platform")
    #st.caption("Reverse engineer legacy and target insurance systems, collate structured specs, and highlight migration gaps.")

    default_legacy_code = str(settings.sample_inputs_dir / "legacy" / "quote_generation" / "vb_code")
    default_legacy_sql = str(settings.sample_inputs_dir / "legacy" / "quote_generation" / "sql")
    default_target_code = str(settings.sample_inputs_dir / "target" / "quote_generation")
    default_target_sql = str(settings.sample_inputs_dir / "target" / "quote_generation" / "sql")
    model_options = MODEL_OPTIONS if settings.model in MODEL_OPTIONS else [settings.model, *MODEL_OPTIONS]

    with st.sidebar:
        st.markdown("## Control Center")
        st.caption("Configure inputs, start the workflow, and review runtime settings.")
        st.markdown("### Legacy Inputs")
        legacy_code_folder = st.text_input(
            "Legacy source code root",
            value=default_legacy_code,
            help="Point this to the legacy VB code folder. The code reverse pass reads VB/VB.NET files from `vb_code` and ignores SQL.",
        )
        legacy_sql_folder = st.text_input(
            "Legacy SQL folder",
            value=default_legacy_sql,
            help="Point this to the legacy SQL folder only. This is reverse engineered separately from the VB code pass.",
        )
        st.markdown("### Target Inputs")
        target_code_folder = st.text_input(
            "Target source code root",
            value=default_target_code,
            help="Point this to the target code root. The code reverse pass will read Angular/Node files and ignore SQL.",
        )
        target_sql_folder = st.text_input(
            "Target SQL folder",
            value=default_target_sql,
            help="Point this to the target SQL folder only.",
        )
        selected_model = st.selectbox(
            "Model",
            options=model_options,
            index=model_options.index(settings.model),
        )
        cache_enabled = st.toggle(
            "Caching",
            value=settings.cache_enabled,
            help="Controls cache reuse for reverse engineering, gap analysis, requirements, technical specification, forward engineering, and generated target-candidate outputs.",
        )
        run_clicked = st.button("Run Modernization Analysis", type="primary", use_container_width=True)
        st.markdown("### Workflow")
        st.markdown("- Reverse legacy source code")
        st.markdown("- Reverse legacy SQL")
        st.markdown("- Collate legacy canonical specification")
        st.markdown("- Reverse target source code")
        st.markdown("- Reverse target SQL")
        st.markdown("- Collate target canonical specification")
        st.markdown("- Build graphical flow maps")
        st.markdown("- Run gap and compliance analysis")
        if st.session_state.get("analysis_result"):
            st.success("Latest analysis is loaded in the workspace.")

    settings.model = selected_model
    settings.cache_enabled = cache_enabled
    auto_run_analysis = st.session_state.pop("auto_run_analysis", False)

    intro_col, stat_col = st.columns([2, 1])
    with intro_col:
        st.markdown(
            """
            <div class="hero-card">
                <div class="eyebrow">Intelligent Migration</div>
                <div class="hero-title">AI driven - Human assisted platform for application migration to modern platforms</div>
                <div class="hero-copy">
                    Reverse Engineering | Canonicalization | Gap Analysis | Business Requirement Creation | Tech Spec Generation | Forward Engineering
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with stat_col:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Launch Ready</div>
                <div class="muted-copy">Sample folders are preloaded so the platform can be demonstrated immediately.</div>
                <div style="margin-top: 0.85rem;">
                    <span class="status-chip">Legacy VB.NET</span>
                    <span class="status-chip">Sybase SQL</span>
                    <span class="status-chip">Angular</span>
                    <span class="status-chip">Node.js</span>
                    <span class="status-chip">PostgreSQL</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if run_clicked or auto_run_analysis:
        st.session_state.pop("analysis_error", None)
        st.session_state.pop("analysis_trace_dir", None)
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        live_logs_placeholder = st.empty()
        trace_dir = create_run_trace_dir()
        st.session_state["analysis_trace_dir"] = str(trace_dir)
        try:
            progress_bar = progress_placeholder.progress(0, text="Initializing modernization workflow...")
            status_placeholder.info("Preparing artifact discovery and analysis context.")
            write_json_trace(
                trace_dir / "run_context.json",
                {
                    "started_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "legacy_code_folder": legacy_code_folder,
                    "legacy_sql_folder": legacy_sql_folder,
                    "target_code_folder": target_code_folder,
                    "target_sql_folder": target_sql_folder,
                    "model": settings.model,
                    "cache_enabled": settings.cache_enabled,
                },
            )
            result: dict = {}
            for partial_state in stream_workflow(
                legacy_code_folder=legacy_code_folder,
                legacy_sql_folder=legacy_sql_folder,
                target_code_folder=target_code_folder,
                target_sql_folder=target_sql_folder,
                approved_requirements=st.session_state.get("approved_requirements"),
                approved_technical_spec=st.session_state.get("approved_technical_spec"),
                prior_state=st.session_state.get("analysis_result") if auto_run_analysis else None,
            ):
                result = partial_state
                write_run_trace_snapshot(trace_dir, partial_state, "running")
                logs = partial_state.get("logs", [])
                render_live_execution_status(live_logs_placeholder, logs)
                seen = {entry.get("agent") for entry in logs}
                completed = sum(1 for key, _label in WORKFLOW_PHASES if key in seen)
                progress_value = completed / len(WORKFLOW_PHASES)
                current_label = "Building execution plan"
                for key, label in WORKFLOW_PHASES:
                    if key not in seen:
                        current_label = label
                        break
                if logs:
                    status_placeholder.info(logs[-1].get("message", current_label))
                progress_bar.progress(progress_value, text=f"{current_label}...")

            st.session_state["analysis_result"] = result
            sync_approval_state_from_result(result)
            finalize_run_trace(trace_dir, result)
            progress_bar.progress(100, text="Analysis complete.")
            status_placeholder.success(f"Modernization analysis completed successfully. Trace saved to {trace_dir}")
        except Exception as exc:
            st.session_state["analysis_error"] = str(exc)
            write_error_trace(trace_dir, str(exc), result if "result" in locals() else {})
            status_placeholder.error(f"Analysis failed. Trace saved to {trace_dir}")

    if st.session_state.get("analysis_error"):
        st.error(st.session_state["analysis_error"])
    if st.session_state.get("analysis_trace_dir"):
        st.caption(f"Run trace folder: {st.session_state['analysis_trace_dir']}")

    result = st.session_state.get("analysis_result")
    if not result:
        st.markdown("### Ready to analyze")
        st.write("Use the sample folders or point the app at separate source-code and SQL folders for legacy and target systems.")
        return

    sync_approval_state_from_result(result)

    requirements_draft = deep_copy_document(result.get("requirements_draft", {}))
    technical_spec_draft = deep_copy_document(result.get("technical_spec_draft", {}))
    approved_requirements = st.session_state.get("approved_requirements")
    approved_technical_spec = st.session_state.get("approved_technical_spec")

    if approved_requirements:
        result["approved_requirements"] = approved_requirements
        result["requirements_draft"] = approved_requirements
        requirements_draft = deep_copy_document(approved_requirements)
    if approved_technical_spec:
        result["approved_technical_spec"] = approved_technical_spec
        result["technical_spec_draft"] = approved_technical_spec
        technical_spec_draft = deep_copy_document(approved_technical_spec)

    requirements_status = get_approval_status(requirements_draft, PENDING_SME_APPROVAL)
    technical_spec_status = get_approval_status(technical_spec_draft, PENDING_ARCHITECT_APPROVAL)
    generated_target = {"generated_root": "", "generated_files": []}
    forward_comparison_items: list[dict] = []
    if result.get("forward_engineering_output"):
        generated_target = materialize_forward_engineering_output(result.get("forward_engineering_output", {}))
        forward_comparison_items = build_forward_engineering_comparison(
            generated_target.get("generated_files", []),
            target_code_folder,
            target_sql_folder,
        )

    render_phase_progress(result.get("logs", []))

    (
        overview_tab,
        step_outputs_tab,
        legacy_tab,
        target_tab,
        flow_tab,
        comparison_tab,
        gap_tab,
        requirements_tab,
        technical_spec_tab,
        forward_engineering_tab,
        forward_proof_tab,
        logs_tab,
        raw_tab,
    ) = st.tabs(
        [
            "Overview",
            "Step Outputs",
            "Legacy Spec",
            "Target Spec",
            "Flow Maps",
            "Comparison",
            "Gap Analysis",
            "Requirements Draft",
            "Technical Specification Draft",
            "Forward Engineering",
            "Forward Engineering Proof",
            "Execution Logs",
            "Raw JSON",
        ]
    )

    with overview_tab:
        gap_analysis = result.get("gap_analysis", {})
        collated = result.get("collated_spec", {})
        overview_gap_confidence = to_float(gap_analysis.get("confidence", {}).get("gap_confidence", 0.0))
        top1, top2, top3 = st.columns(3)
        with top1:
            render_metric_card("Missing Features", str(len(gap_analysis.get("missing_features", []))), "Feature parity shortfalls")
        with top2:
            render_metric_card("Compliance Gaps", str(len(gap_analysis.get("compliance_gaps", []))), "Regulatory exposures detected")
        with top3:
            render_metric_card("Gap Confidence", f"{overview_gap_confidence:.0%}", "Confidence in assessment quality")

        st.markdown("**Modernization Focus Areas**")
        render_table(collated.get("modernization_focus_areas", []), "No focus areas available.")
        st.markdown("**Key Differences**")
        render_table(collated.get("key_differences", []), "No key differences available.")

    with step_outputs_tab:
        render_step_outputs(result)

    with legacy_tab:
        render_spec(result.get("legacy_spec", {}), "Legacy Insurance System")

    with target_tab:
        render_spec(result.get("target_spec", {}), "Target Insurance System")

    with flow_tab:
        legacy_flow_tab, target_flow_tab = st.tabs(["Legacy Flow Map", "Target Flow Map"])
        with legacy_flow_tab:
            render_flow_map(result.get("legacy_spec", {}).get("flow_map", {}), "Legacy System Flow Map")
        with target_flow_tab:
            render_flow_map(result.get("target_spec", {}).get("flow_map", {}), "Target System Flow Map")

    with comparison_tab:
        render_comparison(result.get("collated_spec", {}), result.get("gap_analysis", {}))

    with gap_tab:
        render_gap(result.get("gap_analysis", {}))

    with requirements_tab:
        render_requirements_document(requirements_draft)
        st.markdown("**SME Review Controls**")
        render_approval_summary("Requirements", requirements_status, st.session_state.get("sme_comments", ""))
        st.text_area(
            "SME comments",
            key="sme_comments",
            height=120,
            placeholder="Capture SME review notes for the requirements draft.",
        )
        approve_col, reject_col = st.columns(2)
        with approve_col:
            if st.button("Approve Requirements", use_container_width=True):
                if requirements_draft:
                    approved_doc = update_document_approval(
                        requirements_draft,
                        SME_APPROVED,
                        st.session_state.get("sme_comments", ""),
                        "SME",
                    )
                    st.session_state["approved_requirements"] = approved_doc
                    st.session_state["approved_technical_spec"] = None
                    st.session_state["analysis_result"]["requirements_draft"] = approved_doc
                    st.session_state["auto_run_analysis"] = True
                    st.success("Requirements approved. Continuing automatically to technical specification generation.")
                    st.rerun()
                else:
                    st.warning("No requirements draft is available yet.")
        with reject_col:
            if st.button("Reject Requirements", use_container_width=True):
                if requirements_draft:
                    rejected_doc = update_document_approval(
                        requirements_draft,
                        SME_REJECTED,
                        st.session_state.get("sme_comments", ""),
                        "SME",
                    )
                    st.session_state["approved_requirements"] = None
                    st.session_state["approved_technical_spec"] = None
                    st.session_state["analysis_result"]["requirements_draft"] = rejected_doc
                    st.warning("Requirements rejected. Run the analysis again to regenerate the draft.")
                    st.rerun()
                else:
                    st.warning("No requirements draft is available yet.")

    with technical_spec_tab:
        if requirements_status != SME_APPROVED:
            st.info("Technical specification is blocked until the requirements draft is SME approved.")
        else:
            render_technical_spec_document(technical_spec_draft)

        st.markdown("**Architect Review Controls**")
        render_approval_summary("Technical Specification", technical_spec_status, st.session_state.get("architect_comments", ""))
        st.text_area(
            "Architect comments",
            key="architect_comments",
            height=120,
            placeholder="Capture architect review notes for the technical specification draft.",
        )
        approve_arch_col, reject_arch_col = st.columns(2)
        with approve_arch_col:
            if st.button("Approve Technical Spec", use_container_width=True):
                if requirements_status != SME_APPROVED:
                    st.warning("Approve the requirements draft first.")
                elif technical_spec_draft:
                    approved_doc = update_document_approval(
                        technical_spec_draft,
                        ARCHITECT_APPROVED,
                        st.session_state.get("architect_comments", ""),
                        "Architect",
                    )
                    st.session_state["approved_technical_spec"] = approved_doc
                    st.session_state["analysis_result"]["technical_spec_draft"] = approved_doc
                    st.session_state["auto_run_analysis"] = True
                    st.success("Technical specification approved. Continuing automatically to forward engineering generation.")
                    st.rerun()
                else:
                    st.warning("No technical specification draft is available yet. Run the analysis after SME approval.")
        with reject_arch_col:
            if st.button("Reject Technical Spec", use_container_width=True):
                if technical_spec_draft:
                    rejected_doc = update_document_approval(
                        technical_spec_draft,
                        ARCHITECT_REJECTED,
                        st.session_state.get("architect_comments", ""),
                        "Architect",
                    )
                    st.session_state["approved_technical_spec"] = None
                    st.session_state["analysis_result"]["technical_spec_draft"] = rejected_doc
                    st.warning("Technical specification rejected. Run the analysis again to regenerate the draft.")
                    st.rerun()
                else:
                    st.warning("No technical specification draft is available yet.")

    with forward_engineering_tab:
        if requirements_status != SME_APPROVED:
            st.info("Forward engineering is blocked until the requirements draft is SME approved.")
        elif technical_spec_status != ARCHITECT_APPROVED:
            st.info("Forward engineering is blocked until the technical specification is architect approved.")
        else:
            render_forward_engineering_summary(
                result.get("forward_engineering_output", {}),
                forward_comparison_items,
                generated_target.get("generated_root", ""),
            )

    with forward_proof_tab:
        if requirements_status != SME_APPROVED:
            st.info("Forward engineering proof is blocked until the requirements draft is SME approved.")
        elif technical_spec_status != ARCHITECT_APPROVED:
            st.info("Forward engineering proof is blocked until the technical specification is architect approved.")
        else:
            render_forward_engineering_proof(forward_comparison_items)

    with logs_tab:
        render_logs(result.get("logs", []))

    with raw_tab:
        st.json(result, expanded=False)


if __name__ == "__main__":
    main()
