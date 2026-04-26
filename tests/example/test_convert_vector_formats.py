from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import run_example

arcpy = pytest.importorskip("arcpy")


def test_convert_vector_formats_runs_and_outputs_match_source_count(tmp_path: Path) -> None:
    proc = run_example("convert_vector_formats.py", tmp_path)
    assert proc.returncode == 0, proc.stderr or proc.stdout

    gdb_src = tmp_path / "vector_convert_src_demo.gdb" / "source_points"
    gdb_out_fc = tmp_path / "vector_convert_out_demo.gdb" / "points_from_gdb"
    gdb_out_shp = tmp_path / "vector_convert_out_demo.gdb" / "points_from_shp"
    shp = tmp_path / "shapefile_out" / "demo_points.shp"
    gpkg_fc = f"{tmp_path / 'demo_vectors.gpkg'}/points_gpkg"
    geojson = tmp_path / "demo_points.geojson"

    assert arcpy.Exists(str(gdb_src))
    expected = int(arcpy.management.GetCount(str(gdb_src))[0])

    for path in (str(gdb_out_fc), str(gdb_out_shp), str(shp), gpkg_fc):
        assert arcpy.Exists(path), f"Missing output: {path}"
        assert int(arcpy.management.GetCount(path)[0]) == expected

    assert geojson.is_file(), f"Missing GeoJSON: {geojson}"
