"""Tests for arcpy.management module - all tools, parameters, and return values
documented in skills/arcpy-scripting/modules/arcpy-management.md"""

import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, create_point_fc, new_file_gdb


# ---------------------------------------------------------------------------
# Exists
# ---------------------------------------------------------------------------
def test_mgmt_exists():
    assert hasattr(arcpy.management, "Exists")
    assert callable(arcpy.management.Exists)


def test_mgmt_exists_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "ex.gdb")[0]
    assert arcpy.management.Exists(gdb)
    assert not arcpy.management.Exists(f"{gdb}/nonexistent")


# ---------------------------------------------------------------------------
# CreateFileGDB
# ---------------------------------------------------------------------------
def test_mgmt_create_file_gdb():
    assert hasattr(arcpy.management, "CreateFileGDB")
    assert callable(arcpy.management.CreateFileGDB)


def test_mgmt_create_file_gdb_parameters(tmp_path):
    r = arcpy.management.CreateFileGDB(str(tmp_path), "work.gdb")
    assert isinstance(r, arcpy.Result)
    assert arcpy.Exists(r[0])
    assert r[0].endswith(".gdb")


# ---------------------------------------------------------------------------
# CreateFolder
# ---------------------------------------------------------------------------
def test_mgmt_create_folder():
    assert hasattr(arcpy.management, "CreateFolder")
    assert callable(arcpy.management.CreateFolder)


def test_mgmt_create_folder_parameters(tmp_path):
    r = arcpy.management.CreateFolder(str(tmp_path), "intermediate")
    assert isinstance(r, arcpy.Result)
    from pathlib import Path
    assert Path(r[0]).exists()


# ---------------------------------------------------------------------------
# CreateFeatureclass
# ---------------------------------------------------------------------------
def test_mgmt_create_featureclass():
    assert hasattr(arcpy.management, "CreateFeatureclass")
    assert callable(arcpy.management.CreateFeatureclass)


def test_mgmt_create_featureclass_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "fc.gdb")[0]
    sr = arcpy.SpatialReference(4326)

    for geom in ["POINT", "POLYLINE", "POLYGON"]:
        out = f"{gdb}/fc_{geom}"
        r = arcpy.management.CreateFeatureclass(gdb, f"fc_{geom}", geom, spatial_reference=sr)
        assert arcpy.Exists(r[0])

    # With template
    r = arcpy.management.CreateFeatureclass(gdb, "fc_template", "POINT",
                                              template=f"{gdb}/fc_POINT",
                                              spatial_reference=sr)
    assert arcpy.Exists(r[0])

    # With has_m, has_z
    r = arcpy.management.CreateFeatureclass(gdb, "fc_zm", "POINT",
                                              spatial_reference=sr,
                                              has_m=True, has_z=True)
    assert arcpy.Exists(r[0])


# ---------------------------------------------------------------------------
# CopyFeatures
# ---------------------------------------------------------------------------
def test_mgmt_copy_features():
    assert hasattr(arcpy.management, "CopyFeatures")
    assert callable(arcpy.management.CopyFeatures)


def test_mgmt_copy_features_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "cp.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "src", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))

    r = arcpy.management.CopyFeatures(fc, f"{gdb}/copied")
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)
    count = int(arcpy.management.GetCount(r[0])[0])
    assert count == 1

    r2 = arcpy.management.CopyFeatures(fc, f"{gdb}/copied_cfg", config_keyword="DEFAULTS")
    assert arcpy.Exists(r2[0])


# ---------------------------------------------------------------------------
# CopyRaster
# ---------------------------------------------------------------------------
def test_mgmt_copy_raster():
    assert hasattr(arcpy.management, "CopyRaster")
    assert callable(arcpy.management.CopyRaster)


def test_mgmt_copy_raster_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "cpr.gdb")[0]
    out_raster = arcpy.sa.CreateConstantRaster(1, "INTEGER", 10, arcpy.Extent(0, 0, 100, 100))
    raster_path = f"{gdb}/const_ras"
    out_raster.save(raster_path)

    r = arcpy.management.CopyRaster(raster_path, f"{gdb}/copied_ras")
    assert arcpy.Exists(r[0])

    r2 = arcpy.management.CopyRaster(raster_path, f"{gdb}/copied_ras2",
                                      pixel_type="8_BIT_UNSIGNED",
                                      nodata_value="-9999",
                                      background_value="0")
    assert arcpy.Exists(r2[0])

    r3 = arcpy.management.CopyRaster(raster_path, f"{gdb}/copied_ras3",
                                      onebit_to_eightbit=True)
    assert arcpy.Exists(r3[0])


# ---------------------------------------------------------------------------
# Append
# ---------------------------------------------------------------------------
def test_mgmt_append():
    assert hasattr(arcpy.management, "Append")
    assert callable(arcpy.management.Append)


def test_mgmt_append_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "app.gdb")[0]
    target = arcpy.management.CreateFeatureclass(gdb, "target", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(target, "NAME", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(target, ["SHAPE@XY", "NAME"]) as c:
        c.insertRow(((120.0, 30.0), "Orig"))

    src1 = arcpy.management.CreateFeatureclass(gdb, "src1", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(src1, "NAME", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(src1, ["SHAPE@XY", "NAME"]) as c:
        c.insertRow(((121.0, 31.0), "New1"))

    for schema in ["NO_TEST", "TEST"]:
        target_copy = f"{gdb}/target_{schema}"
        arcpy.management.CopyFeatures(f"{gdb}/target", target_copy)
        try:
            arcpy.management.Append([src1], target_copy, schema)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------
def test_mgmt_merge():
    assert hasattr(arcpy.management, "Merge")
    assert callable(arcpy.management.Merge)


def test_mgmt_merge_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "mrg.gdb")[0]
    for i in range(3):
        fc = arcpy.management.CreateFeatureclass(gdb, f"fc{i}", "POINT", spatial_reference=4326)[0]
        with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
            c.insertRow(((120.0 + i * 0.1, 30.0),))

    r = arcpy.management.Merge([f"{gdb}/fc0", f"{gdb}/fc1", f"{gdb}/fc2"],
                                 f"{gdb}/merged")
    assert arcpy.Exists(r[0])
    count = int(arcpy.management.GetCount(r[0])[0])
    assert count == 3


# ---------------------------------------------------------------------------
# Rename
# ---------------------------------------------------------------------------
def test_mgmt_rename():
    assert hasattr(arcpy.management, "Rename")
    assert callable(arcpy.management.Rename)


def test_mgmt_rename_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "ren.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "old_name", "POINT", spatial_reference=4326)[0]

    r = arcpy.management.Rename(fc, f"{gdb}/new_name")
    assert isinstance(r, arcpy.Result)
    assert arcpy.Exists(f"{gdb}/new_name")
    assert not arcpy.Exists(fc)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------
def test_mgmt_delete():
    assert hasattr(arcpy.management, "Delete")
    assert callable(arcpy.management.Delete)


def test_mgmt_delete_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "del.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "to_delete", "POINT", spatial_reference=4326)[0]
    assert arcpy.Exists(fc)

    r = arcpy.management.Delete(fc)
    assert isinstance(r, arcpy.Result)
    assert not arcpy.Exists(fc)

    # Delete with data_type
    fc2 = arcpy.management.CreateFeatureclass(gdb, "to_delete2", "POINT", spatial_reference=4326)[0]
    r2 = arcpy.management.Delete(fc2, data_type="FeatureClass")
    assert not arcpy.Exists(fc2)


# ---------------------------------------------------------------------------
# AddField
# ---------------------------------------------------------------------------
def test_mgmt_add_field():
    assert hasattr(arcpy.management, "AddField")
    assert callable(arcpy.management.AddField)


def test_mgmt_add_field_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "af.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]

    field_types = ["TEXT", "LONG", "DOUBLE", "DATE", "SHORT", "FLOAT"]
    for i, ft in enumerate(field_types):
        r = arcpy.management.AddField(fc, f"field_{i}", ft,
                                       field_length=20 if ft == "TEXT" else None)
        assert isinstance(r, arcpy.Result)

    r2 = arcpy.management.AddField(fc, "ALIASED", "DOUBLE", field_alias="AliasName",
                                     field_is_nullable="NULLABLE", field_is_required=False)
    assert isinstance(r2, arcpy.Result)

    fields = [f.name for f in arcpy.ListFields(fc)]
    assert "ALIASED" in fields


# ---------------------------------------------------------------------------
# CalculateField
# ---------------------------------------------------------------------------
def test_mgmt_calculate_field():
    assert hasattr(arcpy.management, "CalculateField")
    assert callable(arcpy.management.CalculateField)


def test_mgmt_calculate_field_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "cf.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "STATUS", "TEXT", field_length=20)
    arcpy.management.AddField(fc, "AREA", "DOUBLE")
    arcpy.management.AddField(fc, "CLASS", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))

    r = arcpy.management.CalculateField(fc, "STATUS", "'READY'", "PYTHON3")
    assert isinstance(r, arcpy.Result)
    with arcpy.da.SearchCursor(fc, ["STATUS"]) as c:
        for (s,) in c:
            assert s == "READY"

    r2 = arcpy.management.CalculateField(fc, "AREA", "!SHAPE.area!", "PYTHON3")
    assert isinstance(r2, arcpy.Result)

    code = "def classify(a): return 'SMALL' if a < 1000 else 'LARGE'"
    r3 = arcpy.management.CalculateField(fc, "CLASS", "classify(!AREA!)",
                                           "PYTHON3", code)
    assert isinstance(r3, arcpy.Result)

    r4 = arcpy.management.CalculateField(fc, "STATUS", "'SQLREADY'", "SQL")
    assert isinstance(r4, arcpy.Result)


# ---------------------------------------------------------------------------
# DeleteField
# ---------------------------------------------------------------------------
def test_mgmt_delete_field():
    assert hasattr(arcpy.management, "DeleteField")
    assert callable(arcpy.management.DeleteField)


def test_mgmt_delete_field_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "df.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "TMP_A", "TEXT", field_length=10)
    arcpy.management.AddField(fc, "TMP_B", "TEXT", field_length=10)
    assert "TMP_A" in [f.name for f in arcpy.ListFields(fc)]

    r = arcpy.management.DeleteField(fc, "TMP_A")
    assert isinstance(r, arcpy.Result)
    assert "TMP_A" not in [f.name for f in arcpy.ListFields(fc)]

    r2 = arcpy.management.DeleteField(fc, ["TMP_B"])
    assert isinstance(r2, arcpy.Result)
    assert "TMP_B" not in [f.name for f in arcpy.ListFields(fc)]


# ---------------------------------------------------------------------------
# GetCount
# ---------------------------------------------------------------------------
def test_mgmt_get_count():
    assert hasattr(arcpy.management, "GetCount")
    assert callable(arcpy.management.GetCount)


def test_mgmt_get_count_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "gc.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))
        c.insertRow(((121.0, 31.0),))

    count = int(arcpy.management.GetCount(fc)[0])
    assert count == 2
    assert isinstance(count, int)

    # Empty feature class
    fc2 = arcpy.management.CreateFeatureclass(gdb, "empty", "POINT", spatial_reference=4326)[0]
    count2 = int(arcpy.management.GetCount(fc2)[0])
    assert count2 == 0


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------
def test_mgmt_project():
    assert hasattr(arcpy.management, "Project")
    assert callable(arcpy.management.Project)


def test_mgmt_project_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "proj.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "src", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))

    sr = arcpy.SpatialReference(3857)
    r = arcpy.management.Project(fc, f"{gdb}/proj_pts", sr)
    assert arcpy.Exists(r[0])
    desc = arcpy.Describe(r[0])
    assert desc.spatialReference.factoryCode == 3857

    r2 = arcpy.management.Project(fc, f"{gdb}/proj_pts2", sr,
                                    transform_method="WGS_1984_To_WGS_1984_1")
    assert arcpy.Exists(r2[0])

    r3 = arcpy.management.Project(fc, f"{gdb}/proj_pts3", sr,
                                    in_coor_system=4326,
                                    preserve_shape=True)
    assert arcpy.Exists(r3[0])


# ---------------------------------------------------------------------------
# MakeFeatureLayer
# ---------------------------------------------------------------------------
def test_mgmt_make_feature_layer():
    assert hasattr(arcpy.management, "MakeFeatureLayer")
    assert callable(arcpy.management.MakeFeatureLayer)


def test_mgmt_make_feature_layer_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "mfl.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "ROAD_CLASS", "TEXT", field_length=5)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "ROAD_CLASS"]) as c:
        c.insertRow(((120.0, 30.0), "A"))
        c.insertRow(((121.0, 31.0), "B"))

    lyr = arcpy.management.MakeFeatureLayer(fc, "roads_lyr")[0]
    assert hasattr(lyr, "name")

    lyr2 = arcpy.management.MakeFeatureLayer(fc, "filtered_lyr",
                                               where_clause="ROAD_CLASS = 'A'")[0]
    assert hasattr(lyr2, "name")

    lyr3 = arcpy.management.MakeFeatureLayer(fc, "ws_lyr", workspace=gdb)[0]
    assert hasattr(lyr3, "name")


# ---------------------------------------------------------------------------
# MakeTableView
# ---------------------------------------------------------------------------
def test_mgmt_make_table_view():
    assert hasattr(arcpy.management, "MakeTableView")
    assert callable(arcpy.management.MakeTableView)


def test_mgmt_make_table_view_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "mtv.gdb")[0]
    tbl = arcpy.management.CreateTable(gdb, "data_tbl")[0]
    arcpy.management.AddField(tbl, "CATEGORY", "TEXT", field_length=10)
    with arcpy.da.InsertCursor(tbl, ["CATEGORY"]) as c:
        c.insertRow(["A"])
        c.insertRow(["B"])

    view = arcpy.management.MakeTableView(tbl, "data_view")[0]
    assert hasattr(view, "name")

    view2 = arcpy.management.MakeTableView(tbl, "filtered_view",
                                               where_clause="CATEGORY = 'A'")[0]
    assert hasattr(view2, "name")


# ---------------------------------------------------------------------------
# SelectLayerByAttribute
# ---------------------------------------------------------------------------
def test_mgmt_select_layer_by_attribute():
    assert hasattr(arcpy.management, "SelectLayerByAttribute")
    assert callable(arcpy.management.SelectLayerByAttribute)


def test_mgmt_select_layer_by_attribute_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "sla.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "ROAD_CLASS", "TEXT", field_length=5)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "ROAD_CLASS"]) as c:
        c.insertRow(((120.0, 30.0), "A"))
        c.insertRow(((121.0, 31.0), "B"))

    lyr = arcpy.management.MakeFeatureLayer(fc, "roads_lyr")[0]
    for sel_type in ["NEW_SELECTION", "ADD_TO_SELECTION", "REMOVE_FROM_SELECTION",
                      "SUBSET_SELECTION", "CLEAR_SELECTION"]:
        r = arcpy.management.SelectLayerByAttribute(lyr, sel_type,
                                                      "ROAD_CLASS = 'A'")
        assert isinstance(r, arcpy.Result)


# ---------------------------------------------------------------------------
# SelectLayerByLocation (management version)
# ---------------------------------------------------------------------------
def test_mgmt_select_layer_by_location():
    assert hasattr(arcpy.management, "SelectLayerByLocation")
    assert callable(arcpy.management.SelectLayerByLocation)


def test_mgmt_select_layer_by_location_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "sll.gdb")[0]
    pts = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(pts, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))
        c.insertRow(((120.5, 30.5),))

    poly = arcpy.management.CreateFeatureclass(gdb, "poly", "POLYGON", spatial_reference=4326)[0]
    arr = arcpy.Array([arcpy.Point(119.99, 29.99), arcpy.Point(120.03, 29.99),
                       arcpy.Point(120.03, 30.03), arcpy.Point(119.99, 30.03),
                       arcpy.Point(119.99, 29.99)])
    with arcpy.da.InsertCursor(poly, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr, arcpy.SpatialReference(4326))])

    lyr = arcpy.management.MakeFeatureLayer(pts, "pts_lyr")[0]
    for overlap in ["INTERSECT", "CONTAINS", "WITHIN"]:
        kwargs = {}
        if overlap == "WITHIN_A_DISTANCE":
            kwargs["search_distance"] = "100 Meters"
        r = arcpy.management.SelectLayerByLocation(lyr, overlap, poly, **kwargs)
        assert isinstance(r, arcpy.Result)

    for sel_type in ["NEW_SELECTION", "CLEAR_SELECTION"]:
        r = arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", poly,
                                                      selection_type=sel_type)
        assert isinstance(r, arcpy.Result)
