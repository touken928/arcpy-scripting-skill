import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, new_file_gdb


def test_arcpy_management_parameters_are_really_usable() -> None:
    with arcgis_temp_workspace() as tmp:
        gdb = new_file_gdb(tmp)
        roads = arcpy.management.CreateFeatureclass(gdb, "roads", "POLYLINE", spatial_reference=4326)[0]
        arcpy.management.AddField(roads, "STATUS", "TEXT", field_length=20, field_is_nullable="NULLABLE")
        arcpy.management.CalculateField(roads, "STATUS", "'READY'", "PYTHON3")
        copied = arcpy.management.CopyFeatures(roads, f"{gdb}/roads_copy")[0]
        count = int(arcpy.management.GetCount(copied)[0])
        assert arcpy.Exists(copied)
        assert count == 0
