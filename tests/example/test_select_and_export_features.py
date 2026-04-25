from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import run_example

arcpy = pytest.importorskip("arcpy")


def test_select_and_export_features_runs_and_selects_expected_rows(tmp_path: Path) -> None:
    proc = run_example("select_and_export_features.py", tmp_path)
    assert proc.returncode == 0, proc.stderr or proc.stdout

    out_fc = f"{tmp_path}/select_export_demo.gdb/selected_points"
    assert arcpy.Exists(out_fc), f"Selected output missing: {out_fc}"
    count = int(arcpy.management.GetCount(out_fc)[0])
    assert count == 3
