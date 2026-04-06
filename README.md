# AI Modernization Platform

Streamlit-based workflow for reverse engineering a legacy insurance application, comparing it with a target implementation, drafting modernization artifacts, and generating forward-engineered outputs with review checkpoints.

## What The App Does

The app walks through a modernization flow in stages:

1. Reverse engineer legacy code and legacy SQL into structured JSON specs.
2. Collate those reverse outputs into a unified legacy specification.
3. Reverse engineer target code and target SQL.
4. Collate those reverse outputs into a unified target specification.
5. Run gap analysis between legacy and target.
6. Draft a BRD-style requirements document.
7. Pause for SME approval.
8. Draft a technical specification.
9. Pause for architect approval.
10. Generate forward-engineered target artifacts.
11. Show proof views and file-level diffs for generated outputs.
12. Optionally run validation to compare the generated target against source behavior and approved artifacts.

## Stack

- Python
- Streamlit
- LangGraph
- OpenAI or Anthropic API
- Pandas
- `python-docx` for Word downloads
- `openpyxl` for Excel exports

## Features

- Reverse engineering for code and SQL inputs
- Separate legacy and target analysis tracks
- Gap analysis with comparison tables and numeric confidence
- SME and architect approval gates
- Forward engineering output generation
- Forward engineering proof view with file diffs
- Validation workflow for generated target artifacts
- Word export for BRD and technical specification
- Excel export for workflow outputs, organized one sheet per major step
- Agent output caching under `outputs/cache/`
- Deterministic mock mode when no API key is configured

## Project Structure

```text
app.py
graph.py
config.py
agents/
prompts/
utils/
sample_inputs/
outputs/
  cache/
  runs/
```

## Input Folder Expectations

The app expects four folders:

- `legacy_code_folder`
- `legacy_sql_folder`
- `target_code_folder`
- `target_sql_folder`

The bundled sample data already follows this shape under `sample_inputs/legacy` and `sample_inputs/target`.

## Setup

1. Clone the repository and open a terminal in the project root.
2. Create a virtual environment.

```bash
python -m venv .venv
```

3. Activate the environment.

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

4. Install dependencies.

```bash
pip install -r requirements.txt
```

## Model Configuration

The app reads API keys from environment variables and lets you choose the model from the UI.

### OpenAI

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_key_here"
```

Optional environment override if you want to prefill the UI model selection:

```powershell
$env:OPENAI_MODEL="gpt-5.4-mini"
```

### Anthropic

```powershell
$env:ANTHROPIC_API_KEY="your_key_here"
```

If no API key is set, the app still runs using deterministic mock outputs so the full workflow can be demonstrated.

## Run The App

Start Streamlit from the project root:

```bash
streamlit run app.py
```

After Streamlit starts, open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Quick Start

1. Start the app with `streamlit run app.py`.
2. Leave the default sample paths in the sidebar.
3. Choose a model in the sidebar if needed.
4. Click `Run Modernization Analysis`.
5. Review the generated outputs in the main workspace sections.

## End-To-End Workflow

### 1. Configure Inputs

Use the sidebar to provide:

- Legacy code folder
- Legacy SQL folder
- Target code folder
- Target SQL folder
- Model selection

You can use the sample folders for a demo run or point the app to your own folders.

### 2. Run Analysis

Click `Run Modernization Analysis`.

The app then processes:

1. Legacy code reverse engineering
2. Legacy SQL reverse engineering
3. Legacy collation
4. Target code reverse engineering
5. Target SQL reverse engineering
6. Target collation
7. Gap analysis
8. Requirements draft generation

At this point the workflow pauses for approval.

### 3. Review Requirements Draft

Open `Requirements Draft` in the workspace.

You can:

- Review the BRD-style output
- Add SME comments
- Approve or reject the draft
- Download the document as a Word file

If you approve the requirements draft, the app automatically resumes and generates the technical specification.

### 4. Review Technical Specification Draft

Open `Technical Specification Draft`.

You can:

- Review the technical design output
- Add architect comments
- Approve or reject the draft
- Download the document as a Word file

If you approve the technical specification, the app automatically resumes and runs forward engineering.

### 5. Review Forward Engineering Output

Open `Forward Engineering`.

This section shows:

- Generated target root
- Added and modified files
- File counts and summary information

The forward-engineering target candidate is created by first copying the existing target folder and then overlaying generated changes on top of it. This gives you a full generated target, not just incremental output files.

### 6. Review Forward Engineering Proof

Open `Forward Engineering Proof`.

This section lets you:

- Select a generated file from a dropdown
- View original content
- View generated content
- View a diff between them

The selected section is preserved across reruns so choosing a file does not bounce you back to the first workspace section.

### 7. Validate Generated Target

From `Forward Engineering`, click `Validate Generated Target`.

Validation compares the generated target against:

- The legacy/source behavior captured earlier
- The approved requirements draft
- The approved technical specification

Results are shown in the `Validation` section with a simplified layout:

- Summary
- Differences
- Suggestions
- Confidence

### 8. Download Outputs

The app supports these downloads:

- BRD Word document from `Requirements Draft`
- Technical specification Word document from `Technical Specification Draft`
- Workflow Excel export from the workspace header

The Excel export is organized as one sheet per major step, with UI-style subsections stacked vertically in each sheet.

## Workspace Sections

The main workspace provides these sections:

- Overview
- Step Outputs
- Legacy Spec
- Target Spec
- Flow Maps
- Comparison
- Gap Analysis
- Requirements Draft
- Technical Specification Draft
- Forward Engineering
- Forward Engineering Proof
- Validation
- Execution Logs
- Raw JSON

## Caching

Agent outputs are cached under `outputs/cache/`.

This helps speed up repeated runs, especially when:

- input folders have not changed
- prompts have not changed
- model behavior is stable

If you change prompt structure or output expectations, you may need to clear stale cache files or rely on the cache-version changes already built into some agents.

## Run Traces

Each run writes trace output under `outputs/runs/`.

Typical files include:

- `run_context.json`
- `latest_state.json`
- `workflow_log.json`
- `final_state.json`
- `error.json` when a run fails

These files are useful for troubleshooting interrupted or partial runs.

## Notes About Approvals

- A fresh manual click on `Run Modernization Analysis` starts a new approval cycle.
- Old approvals are not automatically reused for a new manual run.
- Approving requirements resumes from technical specification generation.
- Approving technical specification resumes from forward engineering.

## Troubleshooting

### Validation Button Appears To Do Nothing

Validation results are shown in the `Validation` section. The app now persists those results across reruns and redirects safely without mutating widget state after creation.

### A Run Starts But Produces No Output

Check the latest folder under `outputs/runs/`. If you see only `run_context.json`, `latest_state.json`, and an empty `workflow_log.json`, the run was likely interrupted before the first workflow step executed.

### Prompt Changes Do Not Seem To Take Effect

Cached outputs may still be in use. Check `outputs/cache/` and rerun after clearing the relevant cache files if needed.

### No API Key Configured

The app falls back to deterministic mock outputs so the UI remains usable for demo and onboarding scenarios.

## Dependencies

Current Python dependencies are:

- `streamlit>=1.42.0`
- `langgraph>=0.2.60`
- `openai>=1.68.2`
- `anthropic>=0.40.0`
- `pandas>=2.2.3`
- `python-docx>=1.1.2`
- `openpyxl>=3.1.5`
