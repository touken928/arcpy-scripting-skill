from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import EXAMPLES_DIR

arcpy = pytest.importorskip("arcpy")


def create_test_points(tmp_path: Path) -> str:
    gpkg = tmp_path / "sample_toolbox_test.gpkg"
    arcpy.management.CreateSQLiteDatabase(str(gpkg), "GEOPACKAGE")
    out_fc = f"{gpkg}/sample_points"
    arcpy.management.CreateFeatureclass(str(gpkg), "sample_points", "POINT", spatial_reference=4326)
    arcpy.management.AddField(out_fc, "NAME", "TEXT", field_length=50)
    rows = [
        ("P1", (120.10, 30.20)),
        ("P2", (120.12, 30.24)),
        ("P3", (120.08, 30.18)),
    ]
    with arcpy.da.InsertCursor(out_fc, ["NAME", "SHAPE@XY"]) as cur:
        for row in rows:
            cur.insertRow(row)
    return out_fc


def test_sample_count_features_toolbox_runs_from_cli_and_importtoolbox(tmp_path: Path) -> None:
    in_features = create_test_points(tmp_path)
    toolbox = EXAMPLES_DIR / "sample_count_features_toolbox.pyt"

    proc = subprocess.run(
        [sys.executable, str(toolbox), "--in-features", in_features],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "Feature count: 3" in proc.stdout

    arcpy.ImportToolbox(str(toolbox), "sample_count")
    result = arcpy.CountFeaturesTool_sample_count(in_features)
    assert int(result.getOutput(0)) == 3
