from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import run_example

arcpy = pytest.importorskip("arcpy")


def _make_source_points_gdb(gdb_folder: Path) -> str:
    gdb_folder.mkdir(parents=True, exist_ok=True)
    gdb = gdb_folder / "vector_src_demo.gdb"
    if arcpy.Exists(str(gdb)):
        arcpy.management.Delete(str(gdb))
    arcpy.management.CreateFileGDB(str(gdb_folder), gdb.name)
    sr = arcpy.SpatialReference(4326)
    fc = f"{gdb}/source_points"
    arcpy.management.CreateFeatureclass(str(gdb), "source_points", "POINT", spatial_reference=sr)
    arcpy.management.AddField(fc, "NAME", "TEXT", field_length=50)
    arcpy.management.AddField(fc, "VALUE", "LONG")
    rows = [
        ("A", 1, (120.10, 30.20)),
        ("B", 2, (120.12, 30.24)),
        ("C", 3, (120.08, 30.18)),
    ]
    with arcpy.da.InsertCursor(fc, ["NAME", "VALUE", "SHAPE@XY"]) as cur:
        for row in rows:
            cur.insertRow(row)
    return fc


def test_convert_vector_formats_outputs_match_source_count(tmp_path: Path) -> None:
    arcpy.env.overwriteOutput = True

    src_fc = _make_source_points_gdb(tmp_path)
    expected = int(arcpy.management.GetCount(src_fc)[0])

    out_gdb_folder = tmp_path / "vector_out"
    out_gdb_folder.mkdir(parents=True, exist_ok=True)
    out_gdb = out_gdb_folder / "vector_convert_out_demo.gdb"
    if arcpy.Exists(str(out_gdb)):
        arcpy.management.Delete(str(out_gdb))
    arcpy.management.CreateFileGDB(str(out_gdb_folder), out_gdb.name)

    shp_dir = tmp_path / "shapefile_out"
    shp_dir.mkdir(parents=True, exist_ok=True)
    shp = shp_dir / "demo_points.shp"

    gpkg_fc = f"{tmp_path / 'demo_vectors.gpkg'}/points_gpkg"
    geojson = tmp_path / "demo_points.geojson"

    assert run_example(
        "convert_vector_formats.pyt",
        ["--tool", "shapefile", "--in-features", src_fc, "--out-shp", str(shp)],
    ).returncode == 0

    assert run_example(
        "convert_vector_formats.pyt",
        [
            "--tool",
            "copy_gdb",
            "--in-features",
            src_fc,
            "--out-workspace",
            str(out_gdb),
            "--out-name",
            "points_from_gdb",
        ],
    ).returncode == 0

    assert run_example(
        "convert_vector_formats.pyt",
        ["--tool", "gpkg", "--in-features", src_fc, "--out-gpkg-layer", gpkg_fc],
    ).returncode == 0

    assert run_example(
        "convert_vector_formats.pyt",
        ["--tool", "geojson", "--in-features", src_fc, "--out-geojson", str(geojson)],
    ).returncode == 0

    gdb_out_fc = f"{out_gdb}/points_from_gdb"
    gdb_out_shp = f"{out_gdb}/points_from_shp"

    assert run_example(
        "convert_vector_formats.pyt",
        [
            "--tool",
            "copy_gdb",
            "--in-features",
            str(shp),
            "--out-workspace",
            str(out_gdb),
            "--out-name",
            "points_from_shp",
        ],
    ).returncode == 0

    assert arcpy.Exists(str(shp))
    for path in (gdb_out_fc, gdb_out_shp, str(shp), gpkg_fc):
        assert arcpy.Exists(path), f"Missing output: {path}"
        assert int(arcpy.management.GetCount(path)[0]) == expected

    assert geojson.is_file(), f"Missing GeoJSON: {geojson}"
