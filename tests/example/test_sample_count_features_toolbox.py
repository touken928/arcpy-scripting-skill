from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import EXAMPLES_DIR, run_example

arcpy = pytest.importorskip("arcpy")


def test_sample_count_features_toolbox_runs_from_cli_and_importtoolbox(tmp_path: Path) -> None:
    proc = run_example("sample_count_features_toolbox.pyt", tmp_path)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "Feature count: 3" in proc.stdout

    in_features = f"{tmp_path}/sample_toolbox_demo.gpkg/sample_points"
    assert arcpy.Exists(in_features), f"Demo input missing: {in_features}"

    toolbox = EXAMPLES_DIR / "sample_count_features_toolbox.pyt"
    arcpy.ImportToolbox(str(toolbox), "sample_count")
    result = arcpy.CountFeaturesTool_sample_count(in_features)
    assert int(result.getOutput(0)) == 3
