import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, create_point_fc, new_file_gdb


def test_arcpy_da_parameters_are_really_usable() -> None:
    with arcgis_temp_workspace() as tmp:
        gdb = new_file_gdb(tmp)
        points = create_point_fc(gdb, "da_pts", with_value=False)

        with arcpy.da.InsertCursor(points, ["SHAPE@XY", "VALUE"]) as cursor:
            cursor.insertRow(((120.0, 30.0), 1.0))
            cursor.insertRow(((120.1, 30.1), 2.0))

        with arcpy.da.UpdateCursor(points, ["VALUE"], "VALUE = 1") as cursor:
            for row in cursor:
                row[0] = 11.0
                cursor.updateRow(row)

        values: list[float] = []
        with arcpy.da.SearchCursor(points, ["VALUE"], sql_clause=(None, "ORDER BY VALUE ASC")) as cursor:
            for (v,) in cursor:
                values.append(float(v))
        assert values == [2.0, 11.0]
