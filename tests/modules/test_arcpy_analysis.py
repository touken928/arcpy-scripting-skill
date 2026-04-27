import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, create_point_fc, create_polygon_fc, new_file_gdb


def test_arcpy_analysis_parameters_are_really_usable() -> None:
    with arcgis_temp_workspace() as tmp:
        gdb = new_file_gdb(tmp)
        points = create_point_fc(gdb, "pts")
        clip_poly = create_polygon_fc(gdb, "clip_poly")
        buffer_out = f"{gdb}/pts_buf"
        clip_out = f"{gdb}/pts_clip"
        arcpy.analysis.Buffer(points, buffer_out, "100 Meters", dissolve_option="ALL")
        arcpy.analysis.Clip(points, clip_poly, clip_out)
        assert arcpy.Exists(buffer_out)
        assert arcpy.Exists(clip_out)
