from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import run_example

import arcpy


def _make_points_with_values(gpkg: Path) -> str:
    arcpy.management.CreateSQLiteDatabase(str(gpkg), "GEOPACKAGE")
    sr = arcpy.SpatialReference(4326)
    fc = f"{gpkg}/input_points"
    arcpy.management.CreateFeatureclass(str(gpkg), "input_points", "POINT", spatial_reference=sr)
    arcpy.management.AddField(fc, "NAME", "TEXT", field_length=50)
    arcpy.management.AddField(fc, "VALUE", "LONG")
    rows = [
        ("P1", 10, (120.10, 30.20)),
        ("P2", 20, (120.12, 30.24)),
        ("P3", 30, (120.08, 30.18)),
        ("P4", 40, (120.15, 30.26)),
    ]
    with arcpy.da.InsertCursor(fc, ["NAME", "VALUE", "SHAPE@XY"]) as cur:
        for row in rows:
            cur.insertRow(row)
    return fc


def test_select_and_export_selects_expected_rows(tmp_path: Path) -> None:
    arcpy.env.overwriteOutput = True
    gpkg = tmp_path / "select_export_work.gpkg"
    in_fc = _make_points_with_values(gpkg)
    out_fc = f"{gpkg}/selected_points"

    proc = run_example(
        "select_export.pyt",
        [
            "--in-features",
            in_fc,
            "--where",
            "VALUE >= 20",
            "--layer-name",
            "tmp_select_lyr",
            "--out-features",
            out_fc,
        ],
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout

    assert arcpy.Exists(out_fc), f"Selected output missing: {out_fc}"
    assert int(arcpy.management.GetCount(out_fc)[0]) == 3
