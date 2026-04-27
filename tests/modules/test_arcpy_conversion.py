import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, create_point_fc, new_file_gdb


def test_arcpy_conversion_parameters_are_really_usable() -> None:
    with arcgis_temp_workspace() as tmp:
        gdb = new_file_gdb(tmp)
        points = create_point_fc(gdb, "src_pts")
        converted = arcpy.conversion.FeatureClassToFeatureClass(points, gdb, "pts_a", "VALUE >= 20")[0]
        out_count = int(arcpy.management.GetCount(converted)[0])
        assert arcpy.Exists(converted)
        assert out_count == 2
