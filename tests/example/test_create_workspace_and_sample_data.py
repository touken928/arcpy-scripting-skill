from __future__ import annotations

import csv
from pathlib import Path

import pytest

from .conftest import run_example

arcpy = pytest.importorskip("arcpy")


def _write_sample_csv(path: Path) -> None:
    rows = [
        {
            "geom_type": "POINT",
            "WKT": "POINT (3 4)",
            "name": "p1",
            "note": "one",
        },
        {
            "geom_type": "LINESTRING",
            "WKT": "LINESTRING (0 0, 2 1, 4 0)",
            "name": "l1",
            "note": "two",
        },
        {
            "geom_type": "POLYGON",
            "WKT": "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))",
            "name": "a1",
            "note": "three",
        },
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["geom_type", "WKT", "name", "note"])
        writer.writeheader()
        writer.writerows(rows)


def test_csv_to_geopackage_imports_point_line_polygon(tmp_path: Path) -> None:
    arcpy.env.overwriteOutput = True
    csv_path = tmp_path / "mixed.csv"
    _write_sample_csv(csv_path)

    gpkg_name = "demo.gpkg"
    proc = run_example(
        "csv_to_geopackage.pyt",
        [
            "--in-csv",
            str(csv_path),
            "--out-folder",
            str(tmp_path),
            "--gpkg-name",
            gpkg_name,
            "--feature-basename",
            "demo_fc",
            "--sr-wkid",
            "4326",
        ],
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout

    gpkg = tmp_path / gpkg_name
    assert arcpy.Exists(str(gpkg)), f"GeoPackage missing: {gpkg}"

    point_fc = f"{gpkg}/demo_fc_point"
    line_fc = f"{gpkg}/demo_fc_line"
    poly_fc = f"{gpkg}/demo_fc_polygon"
    for fc in (point_fc, line_fc, poly_fc):
        assert arcpy.Exists(fc), f"Missing feature class: {fc}"
        assert int(arcpy.management.GetCount(fc)[0]) == 1

    with arcpy.da.SearchCursor(point_fc, ["name", "note"]) as cur:
        name, note = next(iter(cur))
    assert name == "p1" and note == "one"
