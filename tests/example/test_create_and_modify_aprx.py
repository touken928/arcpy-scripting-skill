from __future__ import annotations

import os
from glob import glob
from pathlib import Path

import pytest

from .conftest import run_example

arcpy = pytest.importorskip("arcpy")


def _discover_existing_aprx() -> str | None:
    search_roots = [
        Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "ArcGIS" / "Pro",
        Path.home() / "Documents",
    ]
    for root in search_roots:
        if not root.exists():
            continue
        matches = glob(str(root / "**" / "*.aprx"), recursive=True)
        if matches:
            return matches[0]
    return None


def test_create_and_modify_aprx_runs_and_outputs_projects(tmp_path: Path) -> None:
    aprx_path = _discover_existing_aprx()
    if aprx_path:
        proc = run_example("create_and_modify_aprx.py", tmp_path, ["--in-aprx", aprx_path])
        assert proc.returncode == 0, proc.stderr or proc.stdout

        base_aprx = tmp_path / "base_project.aprx"
        modified_aprx = tmp_path / "modified_project.aprx"

        assert base_aprx.exists(), f"Base APRX missing: {base_aprx}"
        assert modified_aprx.exists(), f"Modified APRX missing: {modified_aprx}"
    else:
        proc = run_example(
            "create_and_modify_aprx.py",
            tmp_path,
            ["--in-aprx", str(tmp_path / "missing.aprx")],
        )
        assert proc.returncode != 0
        assert "Input APRX not found" in (proc.stdout + proc.stderr)
