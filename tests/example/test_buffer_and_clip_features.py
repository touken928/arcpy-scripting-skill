from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import run_example

import arcpy


def _make_points_and_clip_polygon(gpkg: Path) -> tuple[str, str]:
    arcpy.management.CreateSQLiteDatabase(str(gpkg), "GEOPACKAGE")
    sr = arcpy.SpatialReference(4326)

    points_fc = f"{gpkg}/input_points"
    arcpy.management.CreateFeatureclass(str(gpkg), "input_points", "POINT", spatial_reference=sr)
    arcpy.management.AddField(points_fc, "NAME", "TEXT", field_length=50)
    rows = [
        ("P1", (120.10, 30.20)),
        ("P2", (120.12, 30.24)),
        ("P3", (120.08, 30.18)),
        ("P4", (120.15, 30.26)),
    ]
    with arcpy.da.InsertCursor(points_fc, ["NAME", "SHAPE@XY"]) as cur:
        for row in rows:
            cur.insertRow(row)

    clip_fc = f"{gpkg}/clip_boundary"
    arcpy.management.CreateFeatureclass(str(gpkg), "clip_boundary", "POLYGON", spatial_reference=sr)
    ring = arcpy.Array(
        [
            arcpy.Point(120.05, 30.15),
            arcpy.Point(120.20, 30.15),
            arcpy.Point(120.20, 30.30),
            arcpy.Point(120.05, 30.30),
            arcpy.Point(120.05, 30.15),
        ]
    )
    with arcpy.da.InsertCursor(clip_fc, ["SHAPE@"]) as cur:
        cur.insertRow([arcpy.Polygon(ring, sr)])

    return points_fc, clip_fc


def test_buffer_and_clip_runs_and_generates_outputs(tmp_path: Path) -> None:
    arcpy.env.overwriteOutput = True
    gpkg = tmp_path / "buffer_clip_work.gpkg"
    in_points, clip_fc = _make_points_and_clip_polygon(gpkg)

    out_buffer = f"{gpkg}/buffer_result"
    out_clip = f"{gpkg}/clip_result"

    proc = run_example(
        "buffer_clip.pyt",
        [
            "--in-points",
            in_points,
            "--clip-polygon",
            clip_fc,
            "--buffer-distance",
            "200 Meters",
            "--out-buffer",
            out_buffer,
            "--out-clip",
            out_clip,
        ],
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout

    assert arcpy.Exists(out_buffer), f"Buffer output missing: {out_buffer}"
    assert arcpy.Exists(out_clip), f"Clip output missing: {out_clip}"
    assert int(arcpy.management.GetCount(out_buffer)[0]) > 0
    assert int(arcpy.management.GetCount(out_clip)[0]) > 0
