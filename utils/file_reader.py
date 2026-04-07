from __future__ import annotations

from pathlib import Path
from typing import Iterable

try:
    import pandas as pd
except ImportError:  # pragma: no cover - runtime fallback
    pd = None


SUPPORTED_SUFFIXES = {
    ".csv",
    ".xls",
    ".xlsx",
    ".txt",
    ".md",
    ".json",
    ".sql",
    ".vb",
    ".vbnet",
    ".cs",
    ".js",
    ".ts",
    ".tsx",
    ".html",
    ".xml",
    ".yaml",
    ".yml",
}


def read_spreadsheet_file(path: Path, max_chars: int) -> dict:
    if pd is None:
        return {
            "path": str(path),
            "name": path.name,
            "content": "",
            "encoding": None,
            "truncated": False,
            "error": "pandas is required to read spreadsheet files.",
        }

    try:
        workbook = pd.read_excel(path, sheet_name=None)
    except Exception as exc:  # pragma: no cover - parser/library failures
        return {
            "path": str(path),
            "name": path.name,
            "content": "",
            "encoding": None,
            "truncated": False,
            "error": f"Unable to read spreadsheet: {exc}",
        }

    sections: list[str] = []
    for sheet_name, dataframe in workbook.items():
        safe_dataframe = dataframe.fillna("")
        sections.append(f"[Sheet: {sheet_name}]")
        sections.append(safe_dataframe.to_csv(index=False).strip())

    content = "\n\n".join(section for section in sections if section)
    return {
        "path": str(path),
        "name": path.name,
        "content": content[:max_chars],
        "encoding": "spreadsheet",
        "truncated": len(content) > max_chars,
        "error": None,
    }


def read_text_file(path: Path, max_chars: int) -> dict:
    if path.suffix.lower() in {".xls", ".xlsx"}:
        return read_spreadsheet_file(path, max_chars=max_chars)

    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
    for encoding in encodings:
        try:
            content = path.read_text(encoding=encoding, errors="strict")
            return {
                "path": str(path),
                "name": path.name,
                "content": content[:max_chars],
                "encoding": encoding,
                "truncated": len(content) > max_chars,
                "error": None,
            }
        except (UnicodeDecodeError, OSError):
            continue

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return {
            "path": str(path),
            "name": path.name,
            "content": content[:max_chars],
            "encoding": "utf-8-replace",
            "truncated": len(content) > max_chars,
            "error": "Recovered with replacement decoding.",
        }
    except OSError as exc:
        return {
            "path": str(path),
            "name": path.name,
            "content": "",
            "encoding": None,
            "truncated": False,
            "error": f"Unable to read file: {exc}",
        }


def read_folder(
    folder_path: str | Path,
    max_files: int,
    max_chars: int,
    include_suffixes: Iterable[str] | None = None,
    exclude_suffixes: Iterable[str] | None = None,
) -> dict:
    folder = Path(folder_path)
    if not folder.exists():
        return {"folder": str(folder), "files": [], "errors": [f"Folder not found: {folder}"]}
    if not folder.is_dir():
        return {"folder": str(folder), "files": [], "errors": [f"Not a directory: {folder}"]}

    include_set = {suffix.lower() for suffix in include_suffixes} if include_suffixes else None
    exclude_set = {suffix.lower() for suffix in exclude_suffixes} if exclude_suffixes else set()

    files = []
    errors: list[str] = []
    candidate_paths = sorted(
        path
        for path in folder.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_SUFFIXES
        and (include_set is None or path.suffix.lower() in include_set)
        and path.suffix.lower() not in exclude_set
    )

    for path in candidate_paths[:max_files]:
        data = read_text_file(path, max_chars=max_chars)
        files.append(data)
        if data["error"]:
            errors.append(f"{path.name}: {data['error']}")

    skipped = len(candidate_paths) - len(files)
    if skipped > 0:
        errors.append(f"Skipped {skipped} files because the folder exceeded the max file limit.")

    if not files and not errors:
        errors.append("No supported files found in folder.")

    return {"folder": str(folder), "files": files, "errors": errors}
