from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import run_example

arcpy = pytest.importorskip("arcpy")


def test_batch_project_featureclasses_runs_and_projects_featureclasses(tmp_path: Path) -> None:
    proc = run_example("batch_project_featureclasses.py", tmp_path)
    assert proc.returncode == 0, proc.stderr or proc.stdout

    out_gdb = f"{tmp_path}/project_out_demo.gdb"
    out_points = f"{out_gdb}/cities_prj"
    out_lines = f"{out_gdb}/roads_prj"

    assert arcpy.Exists(out_points), f"Projected points missing: {out_points}"
    assert arcpy.Exists(out_lines), f"Projected lines missing: {out_lines}"
    assert int(arcpy.management.GetCount(out_points)[0]) == 2
    assert int(arcpy.management.GetCount(out_lines)[0]) == 1
