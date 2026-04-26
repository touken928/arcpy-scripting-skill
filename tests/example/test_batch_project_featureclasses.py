from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import run_example

arcpy = pytest.importorskip("arcpy")


def _make_src_workspace(gpkg: Path) -> None:
    arcpy.management.CreateSQLiteDatabase(str(gpkg), "GEOPACKAGE")
    sr = arcpy.SpatialReference(4326)

    points_fc = f"{gpkg}/cities"
    arcpy.management.CreateFeatureclass(str(gpkg), "cities", "POINT", spatial_reference=sr)
    with arcpy.da.InsertCursor(points_fc, ["SHAPE@XY"]) as cur:
        cur.insertRow(((120.10, 30.20),))
        cur.insertRow(((120.18, 30.22),))

    lines_fc = f"{gpkg}/roads"
    arcpy.management.CreateFeatureclass(str(gpkg), "roads", "POLYLINE", spatial_reference=sr)
    line = arcpy.Polyline(
        arcpy.Array([arcpy.Point(120.00, 30.10), arcpy.Point(120.25, 30.28)]),
        sr,
    )
    with arcpy.da.InsertCursor(lines_fc, ["SHAPE@"]) as cur:
        cur.insertRow([line])


def test_batch_project_projects_featureclasses(tmp_path: Path) -> None:
    arcpy.env.overwriteOutput = True
    in_gpkg = tmp_path / "project_in.gpkg"
    out_gpkg = tmp_path / "project_out.gpkg"
    _make_src_workspace(in_gpkg)
    arcpy.management.CreateSQLiteDatabase(str(out_gpkg), "GEOPACKAGE")

    proc = run_example(
        "batch_project.pyt",
        [
            "--in-workspace",
            str(in_gpkg),
            "--out-workspace",
            str(out_gpkg),
            "--wkid",
            "3857",
            "--suffix",
            "_prj",
        ],
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout

    out_points = f"{out_gpkg}/cities_prj"
    out_lines = f"{out_gpkg}/roads_prj"

    assert arcpy.Exists(out_points), f"Projected points missing: {out_points}"
    assert arcpy.Exists(out_lines), f"Projected lines missing: {out_lines}"
    assert int(arcpy.management.GetCount(out_points)[0]) == 2
    assert int(arcpy.management.GetCount(out_lines)[0]) == 1
