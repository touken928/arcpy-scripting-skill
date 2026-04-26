from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import run_example

arcpy = pytest.importorskip("arcpy")


def test_create_workspace_and_sample_data_runs_and_outputs_valid_data(tmp_path: Path) -> None:
    proc = run_example("create_workspace_and_sample_data.py", tmp_path)
    assert proc.returncode == 0, proc.stderr or proc.stdout

    out_fc = f"{tmp_path}/demo.gpkg/sample_points"
    assert arcpy.Exists(out_fc), f"Output feature class missing: {out_fc}"
    count = int(arcpy.management.GetCount(out_fc)[0])
    assert count == 4
