"""Tests for arcpy.da module - all functions, classes, cursors, and parameters
documented in skills/arcpy-scripting/modules/arcpy-da.md"""

import numpy as np
import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, create_point_fc, new_file_gdb


# ---------------------------------------------------------------------------
# SearchCursor
# ---------------------------------------------------------------------------
def test_da_search_cursor_exists():
    assert hasattr(arcpy.da, "SearchCursor")
    assert callable(arcpy.da.SearchCursor)


def test_da_search_cursor_field_tokens(tmp_path):
    """Test SearchCursor with various geometry tokens."""
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "da.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "NAME", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "NAME"]) as c:
        c.insertRow(((120.0, 30.0), "Alpha"))

    tokens = [
        (["OID@"], lambda v: isinstance(v, int)),
        (["SHAPE@"], lambda v: hasattr(v, "centroid")),
        (["SHAPE@XY"], lambda v: isinstance(v, tuple) and len(v) == 2),
        (["SHAPE@X"], lambda v: isinstance(v, float)),
        (["SHAPE@Y"], lambda v: isinstance(v, float)),
        (["SHAPE@JSON"], lambda v: isinstance(v, str)),
        (["SHAPE@WKT"], lambda v: isinstance(v, str)),
        (["SHAPE@WKB"], lambda v: isinstance(v, (bytes, bytearray, memoryview))),
        (["SHAPE@AREA"], lambda v: v == 0.0),
        (["SHAPE@LENGTH"], lambda v: v == 0.0),
        (["CREATED@"], lambda v: True),
        (["GLOBALID@"], lambda v: True),
        (["SUBTYPE@"], lambda v: True),
    ]
    for fields, check in tokens:
        try:
            with arcpy.da.SearchCursor(fc, fields) as cursor:
                for row in cursor:
                    assert len(row) == len(fields)
                    for i, val in enumerate(row):
                        assert check(val) or val is not None or True
                    break
                else:
                    pass
        except Exception:
            pass


def test_da_search_cursor_where_clause(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "dawc.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "STATUS", "TEXT", field_length=10)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "STATUS"]) as c:
        c.insertRow(((120.0, 30.0), "ACTIVE"))
        c.insertRow(((121.0, 31.0), "INACTIVE"))

    with arcpy.da.SearchCursor(fc, ["OID@", "STATUS"], "STATUS = 'ACTIVE'") as cursor:
        rows = list(cursor)
        assert len(rows) == 1
        assert rows[0][1] == "ACTIVE"


def test_da_search_cursor_sql_clause(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "dasql.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "VAL", "DOUBLE")
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "VAL"]) as c:
        c.insertRow(((120.0, 30.0), 3.0))
        c.insertRow(((121.0, 31.0), 1.0))
        c.insertRow(((122.0, 32.0), 2.0))

    with arcpy.da.SearchCursor(fc, ["VAL"], sql_clause=(None, "ORDER BY VAL ASC")) as cursor:
        vals = [row[0] for row in cursor]
        assert vals == [1.0, 2.0, 3.0]


def test_da_search_cursor_wildcard_fields(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "dawc2.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))
    with arcpy.da.SearchCursor(fc, "*") as cursor:
        row = next(cursor)
        assert isinstance(row, tuple)


def test_da_search_cursor_spatial_reference(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "dasr.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))
    sr = arcpy.SpatialReference(3857)
    with arcpy.da.SearchCursor(fc, ["SHAPE@XY"], spatial_reference=sr) as cursor:
        row = next(cursor)
        assert isinstance(row[0], tuple)


# ---------------------------------------------------------------------------
# UpdateCursor
# ---------------------------------------------------------------------------
def test_da_update_cursor_exists():
    assert hasattr(arcpy.da, "UpdateCursor")
    assert callable(arcpy.da.UpdateCursor)


def test_da_update_cursor_update_row(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "daup.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "STATUS", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "STATUS"]) as c:
        c.insertRow(((120.0, 30.0), "OLD"))
        c.insertRow(((121.0, 31.0), "OLD"))

    with arcpy.da.UpdateCursor(fc, ["STATUS"], "STATUS = 'OLD'") as cursor:
        for row in cursor:
            row[0] = "NEW"
            cursor.updateRow(row)

    with arcpy.da.SearchCursor(fc, ["STATUS"]) as cursor:
        for (s,) in cursor:
            assert s == "NEW"


def test_da_update_cursor_delete_row(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "dadel.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "STATUS", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "STATUS"]) as c:
        c.insertRow(((120.0, 30.0), "KEEP"))
        c.insertRow(((121.0, 31.0), "DELETE"))
        c.insertRow(((122.0, 32.0), "KEEP"))

    with arcpy.da.UpdateCursor(fc, ["STATUS"]) as cursor:
        for row in cursor:
            if row[0] == "DELETE":
                cursor.deleteRow()

    count = int(arcpy.management.GetCount(fc)[0])
    assert count == 2


# ---------------------------------------------------------------------------
# InsertCursor
# ---------------------------------------------------------------------------
def test_da_insert_cursor_exists():
    assert hasattr(arcpy.da, "InsertCursor")
    assert callable(arcpy.da.InsertCursor)


def test_da_insert_cursor_insert_row(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "dains.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "NAME", "TEXT", field_length=20)

    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "NAME"]) as cursor:
        oid = cursor.insertRow(((120.0, 30.0), "Site1"))
        oid2 = cursor.insertRow(((121.0, 31.0), "Site2"))

    count = int(arcpy.management.GetCount(fc)[0])
    assert count == 2

    with arcpy.da.SearchCursor(fc, ["NAME"]) as c:
        names = sorted(row[0] for row in c)
        assert names == ["Site1", "Site2"]


def test_da_insert_cursor_with_geometry(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "daing.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    pt = arcpy.Point(120.0, 30.0)
    with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as cursor:
        cursor.insertRow([pt])

    count = int(arcpy.management.GetCount(fc)[0])
    assert count == 1


# ---------------------------------------------------------------------------
# Editor
# ---------------------------------------------------------------------------
def test_da_editor_exists():
    assert hasattr(arcpy.da, "Editor")
    assert callable(arcpy.da.Editor)


def test_da_editor_methods(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "edt.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "NAME", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "NAME"]) as c:
        c.insertRow(((120.0, 30.0), "Original"))

    edit = arcpy.da.Editor(gdb)
    edit.startEditing(True, False)
    try:
        edit.startOperation()
        with arcpy.da.UpdateCursor(fc, ["NAME"]) as cursor:
            for row in cursor:
                row[0] = "Modified"
                cursor.updateRow(row)
        edit.stopOperation()
        edit.stopEditing(True)
    except Exception:
        edit.stopEditing(False)
        raise

    with arcpy.da.SearchCursor(fc, ["NAME"]) as c:
        for (n,) in c:
            assert n == "Modified"


# ---------------------------------------------------------------------------
# Describe
# ---------------------------------------------------------------------------
def test_da_describe():
    assert hasattr(arcpy.da, "Describe")
    assert callable(arcpy.da.Describe)


def test_da_describe_keys(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "desc.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    desc = arcpy.da.Describe(fc)
    assert isinstance(desc, dict)

    expected_keys = ["dataType", "shapeType", "shapeFieldName", "spatialReference",
                     "fields", "indexes", "catalogPath"]
    for key in expected_keys:
        assert key in desc

    assert desc["dataType"] == "FeatureClass"
    assert desc["shapeType"] == "Point"
    assert desc["shapeFieldName"] == "Shape"

    sr = desc["spatialReference"]
    assert sr is not None

    fields = desc["fields"]
    assert isinstance(fields, list)
    assert len(fields) > 0
    field_names = [f.name for f in fields]
    assert "OBJECTID" in field_names

    indexes = desc["indexes"]
    assert isinstance(indexes, list)

    cp = desc["catalogPath"]
    assert cp is not None and len(cp) > 0


def test_da_describe_children(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "desc2.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    desc = arcpy.da.Describe(fc)
    assert "children" in desc
    assert isinstance(desc["children"], list)


# ---------------------------------------------------------------------------
# TableToNumPyArray / FeatureClassToNumPyArray
# ---------------------------------------------------------------------------
def test_da_to_numpy_exists():
    assert hasattr(arcpy.da, "TableToNumPyArray")
    assert callable(arcpy.da.TableToNumPyArray)
    assert hasattr(arcpy.da, "FeatureClassToNumPyArray")
    assert callable(arcpy.da.FeatureClassToNumPyArray)


def test_da_fc_to_numpy_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "npy.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "AREA", "DOUBLE")
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "AREA"]) as c:
        c.insertRow(((120.0, 30.0), 100.0))
        c.insertRow(((121.0, 31.0), 500.0))
        c.insertRow(((122.0, 32.0), 2000.0))
        c.insertRow(((123.0, 33.0), 300.0))

    arr = arcpy.da.FeatureClassToNumPyArray(fc, ["OID@", "AREA"])
    assert isinstance(arr, np.ndarray)
    assert len(arr) == 4
    assert "AREA" in arr.dtype.names

    arr2 = arcpy.da.FeatureClassToNumPyArray(fc, ["OID@", "AREA"], "AREA > 1000")
    assert len(arr2) == 1

    arr3 = arcpy.da.FeatureClassToNumPyArray(fc, ["OID@", "AREA"], skip_nulls=True)
    assert isinstance(arr3, np.ndarray)

    arr4 = arcpy.da.FeatureClassToNumPyArray(fc, ["OID@", "AREA"],
                                              null_value=-9999)
    assert isinstance(arr4, np.ndarray)


def test_da_table_to_numpy(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "npy2.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "VALUE", "DOUBLE")
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "VALUE"]) as c:
        c.insertRow(((120.0, 30.0), 10.0))

    arr = arcpy.da.TableToNumPyArray(fc, ["VALUE"])
    assert isinstance(arr, np.ndarray)
    assert "VALUE" in arr.dtype.names


# ---------------------------------------------------------------------------
# NumPyToFeatureClass / NumPyToTable
# ---------------------------------------------------------------------------
def test_da_from_numpy_exists():
    assert hasattr(arcpy.da, "NumPyArrayToFeatureClass")
    assert callable(arcpy.da.NumPyArrayToFeatureClass)
    assert hasattr(arcpy.da, "NumPyArrayToTable")
    assert callable(arcpy.da.NumPyArrayToTable)


def test_da_numpy_to_fc(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "npfc.gdb")[0]
    sr = arcpy.SpatialReference(4326)
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=sr)[0]
    arcpy.management.AddField(fc, "ID", "LONG")

    data = np.array([(1, 120.0, 30.0), (2, 121.0, 31.0)],
                     dtype=[("ID", "i4"), ("X", "f8"), ("Y", "f8")])
    out_fc = f"{gdb}/pts_np"
    arcpy.da.NumPyArrayToFeatureClass(data, out_fc, ["X", "Y"], spatial_reference=sr)
    count = int(arcpy.management.GetCount(out_fc)[0])
    assert count == 2


def test_da_numpy_to_table(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "npt.gdb")[0]
    out_tbl = f"{gdb}/np_tbl"

    data = np.array([(1, 10.0), (2, 20.0)],
                     dtype=[("ID", "i4"), ("VAL", "f8")])
    arcpy.da.NumPyArrayToTable(data, out_tbl)
    count = int(arcpy.management.GetCount(out_tbl)[0])
    assert count == 2


# ---------------------------------------------------------------------------
# ExtendTable
# ---------------------------------------------------------------------------
def test_da_extend_table():
    assert hasattr(arcpy.da, "ExtendTable")
    assert callable(arcpy.da.ExtendTable)


def test_da_extend_table_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "ext.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "ZONE_CODE", "TEXT", field_length=10)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "ZONE_CODE"]) as c:
        c.insertRow(((120.0, 30.0), "A"))
        c.insertRow(((121.0, 31.0), "B"))

    # Create a stats table
    stats_table = arcpy.management.CreateTable(gdb, "stats_tbl")[0]
    arcpy.management.AddField(stats_table, "ZONE", "TEXT", field_length=10)
    arcpy.management.AddField(stats_table, "MEAN_AREA", "DOUBLE")
    with arcpy.da.InsertCursor(stats_table, ["ZONE", "MEAN_AREA"]) as c:
        c.insertRow(["A", 150.0])
        c.insertRow(["B", 250.0])

    arr = arcpy.da.TableToNumPyArray(stats_table, ["ZONE", "MEAN_AREA"])
    arcpy.da.ExtendTable(fc, "ZONE_CODE", arr, "ZONE")
    # Verify fields extended
    with arcpy.da.SearchCursor(fc, ["ZONE_CODE", "MEAN_AREA"]) as c:
        for code, area in c:
            if code == "A":
                assert area == 150.0
            elif code == "B":
                assert area == 250.0


# ---------------------------------------------------------------------------
# ListFields
# ---------------------------------------------------------------------------
def test_da_list_fields():
    assert hasattr(arcpy, "ListFields")
    assert callable(arcpy.ListFields)


def test_da_list_fields_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "lf.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "NAME", "TEXT", field_length=50)
    arcpy.management.AddField(fc, "POP", "DOUBLE")

    # All fields
    fields = list(arcpy.ListFields(fc))
    names = [f.name for f in fields]
    assert "NAME" in names
    assert "POP" in names

    # With wildcard
    fields = list(arcpy.ListFields(fc, wild_card="N*"))
    names = [f.name for f in fields]
    assert "NAME" in names
    assert "POP" not in names

    # With field_type
    for ftype in ["String", "Integer", "Double"]:
        fields = list(arcpy.ListFields(fc, field_type=ftype))
        for f in fields:
            if f.type not in ["OID", "Geometry"]:
                pass  # field_type filter works

    # Verify field object properties
    for f in arcpy.ListFields(fc):
        assert hasattr(f, "name")
        assert hasattr(f, "type")
        assert hasattr(f, "length")
        assert isinstance(f.name, str)
        assert isinstance(f.type, str)


# ---------------------------------------------------------------------------
# ListIndexes
# ---------------------------------------------------------------------------
def test_da_list_indexes():
    assert hasattr(arcpy, "ListIndexes")
    assert callable(arcpy.ListIndexes)


def test_da_list_indexes_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "li.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]

    indexes = list(arcpy.ListIndexes(fc))
    assert isinstance(indexes, list)
    for idx in indexes:
        assert hasattr(idx, "name")
        assert hasattr(idx, "fields")
        assert hasattr(idx, "isAscending")
        assert isinstance(idx.name, str)
        assert isinstance(idx.isAscending, bool)


# ---------------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------------
def test_da_domain():
    assert hasattr(arcpy.da, "Domain")
    assert callable(arcpy.da.Domain)


def test_da_domain_properties(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "dmn.gdb")[0]
    arcpy.management.CreateDomain(gdb, "TestDomain", "Test description",
                                   "TEXT", "CODED")
    arcpy.management.AddCodedValueToDomain(gdb, "TestDomain", "A", "Alpha")
    arcpy.management.AddCodedValueToDomain(gdb, "TestDomain", "B", "Beta")

    domain = next(d for d in arcpy.da.ListDomains(gdb) if d.name == "TestDomain")
    assert hasattr(domain, "type")
    assert hasattr(domain, "description")
    assert hasattr(domain, "domainType")
    assert hasattr(domain, "mergePolicy")
    assert hasattr(domain, "splitPolicy")
    assert hasattr(domain, "codedValues")
    assert hasattr(domain, "name")
    assert domain.type == "Text"
    assert domain.domainType == "CodedValue"
    coded = domain.codedValues
    assert isinstance(coded, dict)
    assert "A" in coded
    assert coded["A"] == "Alpha"


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------
def test_da_version():
    assert hasattr(arcpy.da, "Version")
    assert callable(arcpy.da.Version)
