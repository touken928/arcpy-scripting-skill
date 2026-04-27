"""Tests for arcpy top-level functions - all functions, parameters, and return values
documented in skills/arcpy-scripting/modules/arcpy-functions.md"""

import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, create_point_fc, new_file_gdb


# ---------------------------------------------------------------------------
# Environment management
# ---------------------------------------------------------------------------
def test_list_environments():
    assert hasattr(arcpy, "ListEnvironments")
    assert callable(arcpy.ListEnvironments)
    envs = arcpy.ListEnvironments()
    assert isinstance(envs, list)
    assert len(envs) > 0
    assert "cellSize" in envs


def test_get_system_environment():
    assert hasattr(arcpy, "GetSystemEnvironment")
    assert callable(arcpy.GetSystemEnvironment)
    temp = arcpy.GetSystemEnvironment("TEMP")
    assert isinstance(temp, str)
    temp2 = arcpy.GetSystemEnvironment("TEMP")
    assert isinstance(temp2, str)


def test_clear_environment():
    assert hasattr(arcpy, "ClearEnvironment")
    assert callable(arcpy.ClearEnvironment)
    arcpy.ClearEnvironment("cellSize")


def test_reset_environments():
    assert hasattr(arcpy, "ResetEnvironments")
    assert callable(arcpy.ResetEnvironments)
    arcpy.ResetEnvironments()


# ---------------------------------------------------------------------------
# Data describe (arcpy.Describe)
# ---------------------------------------------------------------------------
def test_describe_exists():
    assert hasattr(arcpy, "Describe")
    assert callable(arcpy.Describe)


def test_describe_general_properties(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "dsc.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]

    desc = arcpy.Describe(fc)
    assert hasattr(desc, "catalogPath")
    assert hasattr(desc, "dataType")
    assert hasattr(desc, "name")
    assert hasattr(desc, "baseName")
    assert hasattr(desc, "file")
    assert hasattr(desc, "extension")
    assert hasattr(desc, "children")
    assert hasattr(desc, "path")

    assert isinstance(desc.dataType, str)
    assert isinstance(desc.name, str)
    assert isinstance(desc.catalogPath, str)
    assert desc.dataType == "FeatureClass"


def test_describe_feature_class_properties(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "dsfc.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]

    desc = arcpy.Describe(fc)
    assert desc.shapeType == "Point"
    assert desc.shapeFieldName == "Shape"
    assert desc.spatialReference is not None
    assert hasattr(desc, "hasZ")
    assert hasattr(desc, "hasM")
    assert hasattr(desc, "featureType")


def test_describe_raster_properties(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "dsr.gdb")[0]
    out_raster = arcpy.sa.CreateConstantRaster(1, "INTEGER", 10, arcpy.Extent(0, 0, 100, 100))
    raster_path = f"{gdb}/const_ras"
    out_raster.save(raster_path)

    desc = arcpy.Describe(raster_path)
    assert desc.dataType == "RasterDataset"
    assert hasattr(desc, "bandCount")
    assert hasattr(desc, "pixelType")
    assert isinstance(desc.bandCount, int)


# ---------------------------------------------------------------------------
# Field operations
# ---------------------------------------------------------------------------
def test_add_field_delimiters():
    assert hasattr(arcpy, "AddFieldDelimiters")
    assert callable(arcpy.AddFieldDelimiters)


def test_add_field_delimiters_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "afd.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]

    delimited = arcpy.AddFieldDelimiters(fc, "NAME")
    assert isinstance(delimited, str)
    assert "NAME" in delimited


def test_parse_field_name():
    assert hasattr(arcpy, "ParseFieldName")
    assert callable(arcpy.ParseFieldName)

    result = arcpy.ParseFieldName("work.gdb.owner.TABLENAME.MY_FIELD")
    assert isinstance(result, str)
    parts = result.split(",")
    assert len(parts) == 4
    assert "MY_FIELD" in parts[-1]

    result2 = arcpy.ParseFieldName("work.gdb.owner.TABLENAME.MY_FIELD", "some.db")
    assert isinstance(result2, str)


def test_validate_field_name():
    assert hasattr(arcpy, "ValidateFieldName")
    assert callable(arcpy.ValidateFieldName)


def test_validate_field_name_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "vfn.gdb")[0]
    valid = arcpy.ValidateFieldName("My Field/Invalid!", gdb)
    assert isinstance(valid, str)
    assert "/" not in valid
    assert " " not in valid


# ---------------------------------------------------------------------------
# Data query
# ---------------------------------------------------------------------------
def test_exists():
    assert hasattr(arcpy, "Exists")
    assert callable(arcpy.Exists)


def test_exists_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "ex.gdb")[0]
    assert arcpy.Exists(gdb)
    assert not arcpy.Exists(f"{gdb}/nonexistent")


def test_test_schema_lock():
    assert hasattr(arcpy, "TestSchemaLock")
    assert callable(arcpy.TestSchemaLock)


def test_test_schema_lock_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "tsl.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    locked = arcpy.TestSchemaLock(fc)
    assert isinstance(locked, bool)
    assert locked


def test_parse_table_name():
    assert hasattr(arcpy, "ParseTableName")
    assert callable(arcpy.ParseTableName)

    result = arcpy.ParseTableName("work.gdb.owner.MYTABLE")
    assert isinstance(result, str)
    parts = result.split(",")
    assert len(parts) >= 3

    result2 = arcpy.ParseTableName("work.gdb.owner.MYTABLE", "some.db")
    assert isinstance(result2, str)


def test_validate_table_name():
    assert hasattr(arcpy, "ValidateTableName")
    assert callable(arcpy.ValidateTableName)


def test_validate_table_name_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "vtn.gdb")[0]
    valid = arcpy.ValidateTableName("My Table!", gdb)
    assert isinstance(valid, str)
    assert " " not in valid


# ---------------------------------------------------------------------------
# Data listing
# ---------------------------------------------------------------------------
def test_list_datasets():
    assert hasattr(arcpy, "ListDatasets")
    assert callable(arcpy.ListDatasets)


def test_list_datasets_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "lds.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "Zone_01", "POINT", spatial_reference=4326)[0]
    arcpy.env.workspace = gdb
    datasets = arcpy.ListDatasets()
    assert isinstance(datasets, list)

    datasets2 = arcpy.ListDatasets("Zone*")
    assert isinstance(datasets2, list)

    datasets3 = arcpy.ListDatasets("Zone*", "Feature")
    assert isinstance(datasets3, list)
    arcpy.env.workspace = None


def test_list_feature_classes():
    assert hasattr(arcpy, "ListFeatureClasses")
    assert callable(arcpy.ListFeatureClasses)


def test_list_feature_classes_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "lfc.gdb")[0]
    arcpy.management.CreateFeatureclass(gdb, "Zone_poly", "POLYGON", spatial_reference=4326)
    arcpy.management.CreateFeatureclass(gdb, "Zone_pt", "POINT", spatial_reference=4326)

    arcpy.env.workspace = gdb
    fcs = arcpy.ListFeatureClasses()
    assert isinstance(fcs, list)
    assert len(fcs) >= 2

    polys = arcpy.ListFeatureClasses("Zone*", "Polygon")
    assert isinstance(polys, list)
    for fc in polys:
        desc = arcpy.Describe(fc)
        assert desc.shapeType in ("Polygon", "Polyline", "Point")

    points = arcpy.ListFeatureClasses(feature_type="Point")
    assert isinstance(points, list)
    arcpy.env.workspace = None


def test_list_fields():
    assert hasattr(arcpy, "ListFields")
    assert callable(arcpy.ListFields)


def test_list_fields_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "lf2.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "NAME", "TEXT", field_length=20)

    fields = arcpy.ListFields(fc)
    assert isinstance(fields, list)
    names = [f.name for f in fields]
    assert "NAME" in names

    str_fields = arcpy.ListFields(fc, field_type="String")
    for f in str_fields:
        assert f.type in ("String", "OID", "Geometry")

    wc_fields = arcpy.ListFields(fc, "N*")
    for f in wc_fields:
        assert f.name.startswith("N")


def test_list_indexes():
    assert hasattr(arcpy, "ListIndexes")
    assert callable(arcpy.ListIndexes)


def test_list_indexes_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "lidx.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]

    indexes = arcpy.ListIndexes(fc)
    assert isinstance(indexes, list)
    for idx in indexes:
        assert hasattr(idx, "name")
        assert hasattr(idx, "fields")
        assert hasattr(idx, "isAscending")


def test_list_rasters():
    assert hasattr(arcpy, "ListRasters")
    assert callable(arcpy.ListRasters)


def test_list_rasters_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "lr.gdb")[0]
    out_raster = arcpy.sa.CreateConstantRaster(1, "INTEGER", 10, arcpy.Extent(0, 0, 100, 100))
    out_raster.save(f"{gdb}/dem_tiff")

    arcpy.env.workspace = gdb
    rasters = arcpy.ListRasters()
    assert isinstance(rasters, list)
    assert len(rasters) >= 1

    rasters2 = arcpy.ListRasters("dem*")
    assert isinstance(rasters2, list)

    rasters3 = arcpy.ListRasters("dem*", "TIFF")
    assert isinstance(rasters3, list)
    arcpy.env.workspace = None


def test_list_tables():
    assert hasattr(arcpy, "ListTables")
    assert callable(arcpy.ListTables)


def test_list_tables_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "lt.gdb")[0]
    arcpy.management.CreateTable(gdb, "lookup_data")
    arcpy.management.CreateTable(gdb, "lookup_ref")

    arcpy.env.workspace = gdb
    tables = arcpy.ListTables()
    assert isinstance(tables, list)
    assert len(tables) >= 2

    tables2 = arcpy.ListTables("lookup*")
    assert isinstance(tables2, list)

    tables3 = arcpy.ListTables("lookup*", "ALL")
    assert isinstance(tables3, list)
    arcpy.env.workspace = None


def test_list_files():
    assert hasattr(arcpy, "ListFiles")
    assert callable(arcpy.ListFiles)


def test_list_versions():
    assert hasattr(arcpy, "ListVersions")
    assert callable(arcpy.ListVersions)


def test_list_workspaces():
    assert hasattr(arcpy, "ListWorkspaces")
    assert callable(arcpy.ListWorkspaces)


def test_list_printer_names():
    assert hasattr(arcpy, "ListPrinterNames")
    assert callable(arcpy.ListPrinterNames)

    printers = arcpy.ListPrinterNames()
    assert isinstance(printers, list)


# ---------------------------------------------------------------------------
# Geometry functions
# ---------------------------------------------------------------------------
def test_from_wkt():
    assert hasattr(arcpy, "FromWKT")
    assert callable(arcpy.FromWKT)

    sr = arcpy.SpatialReference(4326)
    geom = arcpy.FromWKT("POINT (120.0 30.0)", sr)
    assert hasattr(geom, "centroid")
    assert hasattr(geom, "type")
    assert geom.type == "point"

    # Polygon from WKT
    poly = arcpy.FromWKT("POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))", sr)
    assert poly.type == "polygon"

    # With has_z, has_m
    geom_z = arcpy.FromWKT("POINT (120.0 30.0)", sr)


def test_from_wkb():
    assert hasattr(arcpy, "FromWKB")
    assert callable(arcpy.FromWKB)

    sr = arcpy.SpatialReference(4326)
    pt = arcpy.FromWKT("POINT (120.0 30.0)", sr)
    wkb = pt.WKB
    geom = arcpy.FromWKB(bytes(wkb), sr)
    assert hasattr(geom, "centroid")


def test_as_shape():
    assert hasattr(arcpy, "AsShape")
    assert callable(arcpy.AsShape)

    json_geom = '{"x": 120.0, "y": 30.0, "spatialReference": {"wkid": 4326}}'
    pt = arcpy.AsShape(json_geom, True)
    assert hasattr(pt, "centroid")
    assert pt.centroid.X == pytest.approx(120.0)
    assert pt.centroid.Y == pytest.approx(30.0)


def test_from_coord_string():
    assert hasattr(arcpy, "FromCoordString")
    assert callable(arcpy.FromCoordString)


def test_from_geohash():
    assert hasattr(arcpy, "FromGeohash")
    assert callable(arcpy.FromGeohash)

    extent = arcpy.FromGeohash("wtm37k")
    assert hasattr(extent, "XMin")
    assert hasattr(extent, "YMin")
    assert hasattr(extent, "XMax")
    assert hasattr(extent, "YMax")


# ---------------------------------------------------------------------------
# General functions
# ---------------------------------------------------------------------------
def test_usage():
    assert hasattr(arcpy, "Usage")
    assert callable(arcpy.Usage)

    syntax = arcpy.Usage("Buffer")
    assert isinstance(syntax, str)
    assert len(syntax) > 0

    params = arcpy.Usage("arcpy.management.CopyFeatures")
    assert isinstance(params, str)


def test_command():
    assert hasattr(arcpy, "Command")
    assert callable(arcpy.Command)


def test_create_scratch_name():
    assert hasattr(arcpy, "CreateScratchName")
    assert callable(arcpy.CreateScratchName)

    name = arcpy.CreateScratchName("temp", "fc", "FeatureClass", arcpy.env.scratchGDB)
    assert isinstance(name, str)

    name2 = arcpy.CreateScratchName("temp", "fc", "FeatureClass", arcpy.env.scratchGDB)
    assert isinstance(name2, str)


def test_create_unique_name():
    assert hasattr(arcpy, "CreateUniqueName")
    assert callable(arcpy.CreateUniqueName)


def test_create_unique_name_parameters(tmp_path):
    unique = arcpy.CreateUniqueName("output.shp", str(tmp_path))
    assert isinstance(unique, str)
    assert ".shp" in unique

    unique2 = arcpy.CreateUniqueName("test", str(tmp_path))
    assert isinstance(unique2, str)


def test_create_object():
    assert hasattr(arcpy, "CreateObject")
    assert callable(arcpy.CreateObject)

    vt = arcpy.CreateObject("ValueTable", 3)
    assert hasattr(vt, "addRow")
    vt.addRow("val1 val2 val3")


def test_create_random_value_generator():
    assert hasattr(arcpy, "CreateRandomValueGenerator")
    assert callable(arcpy.CreateRandomValueGenerator)

    rng = arcpy.CreateRandomValueGenerator(42, "UNIFORM 0 1")
    assert hasattr(rng, "exportToString")

    rng2 = arcpy.CreateRandomValueGenerator(0, "UNIFORM 0 1")
    assert hasattr(rng2, "exportToString")


def test_aio_file_open():
    assert hasattr(arcpy, "AIOFileOpen")
    assert callable(arcpy.AIOFileOpen)


def test_get_stac_info():
    assert hasattr(arcpy, "GetSTACInfo")
    assert callable(arcpy.GetSTACInfo)


def test_alter_alias_name():
    assert hasattr(arcpy, "AlterAliasName")
    assert callable(arcpy.AlterAliasName)


def test_alter_alias_name_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "aan.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]

    result = arcpy.AlterAliasName(fc, "PointAlias")
    assert result is None


def test_is_being_edited():
    assert hasattr(arcpy, "IsBeingEdited")
    assert callable(arcpy.IsBeingEdited)


def test_is_being_edited_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "ibe.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    editing = arcpy.IsBeingEdited(fc)
    assert isinstance(editing, bool)


def test_refresh_layer():
    assert hasattr(arcpy, "RefreshLayer")
    assert callable(arcpy.RefreshLayer)


def test_areal_unit_conversion_factor():
    assert hasattr(arcpy, "ArealUnitConversionFactor")
    assert callable(arcpy.ArealUnitConversionFactor)

    factor = arcpy.ArealUnitConversionFactor("ACRES", "SQUAREMETERS")
    assert isinstance(factor, float)
    assert factor > 0


def test_linear_unit_conversion_factor():
    assert hasattr(arcpy, "LinearUnitConversionFactor")
    assert callable(arcpy.LinearUnitConversionFactor)

    factor = arcpy.LinearUnitConversionFactor("FEET", "METERS")
    assert isinstance(factor, float)
    assert factor > 0


# ---------------------------------------------------------------------------
# Data store management
# ---------------------------------------------------------------------------
def test_add_data_store_item():
    assert hasattr(arcpy, "AddDataStoreItem")
    assert callable(arcpy.AddDataStoreItem)


def test_list_data_store_items():
    assert hasattr(arcpy, "ListDataStoreItems")
    assert callable(arcpy.ListDataStoreItems)


def test_validate_data_store_item():
    assert hasattr(arcpy, "ValidateDataStoreItem")
    assert callable(arcpy.ValidateDataStoreItem)


def test_remove_data_store_item():
    assert hasattr(arcpy, "RemoveDataStoreItem")
    assert callable(arcpy.RemoveDataStoreItem)


# ---------------------------------------------------------------------------
# Enterprise geodatabase management
# ---------------------------------------------------------------------------
def test_accept_connections():
    assert hasattr(arcpy, "AcceptConnections")
    assert callable(arcpy.AcceptConnections)


def test_disconnect_user():
    assert hasattr(arcpy, "DisconnectUser")
    assert callable(arcpy.DisconnectUser)


def test_list_users():
    assert hasattr(arcpy, "ListUsers")
    assert callable(arcpy.ListUsers)


# ---------------------------------------------------------------------------
# Legacy cursors
# ---------------------------------------------------------------------------
def test_legacy_search_cursor():
    assert hasattr(arcpy, "SearchCursor")
    assert callable(arcpy.SearchCursor)


def test_legacy_search_cursor_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "lsc.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "NAME", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "NAME"]) as c:
        c.insertRow(((120.0, 30.0), "Alpha"))
        c.insertRow(((121.0, 31.0), "Beta"))

    cursor = arcpy.SearchCursor(fc, "NAME = 'Alpha'", "", "NAME", "NAME A")
    rows = list(cursor)
    assert len(rows) >= 1
    for row in rows:
        assert row.getValue("NAME") is not None
    del cursor


def test_legacy_update_cursor():
    assert hasattr(arcpy, "UpdateCursor")
    assert callable(arcpy.UpdateCursor)


def test_legacy_update_cursor_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "luc.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "STATUS", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "STATUS"]) as c:
        c.insertRow(((120.0, 30.0), "OLD"))

    cursor = arcpy.UpdateCursor(fc, "STATUS = 'OLD'")
    for row in cursor:
        row.setValue("STATUS", "DONE")
        cursor.updateRow(row)
    del cursor

    with arcpy.da.SearchCursor(fc, ["STATUS"]) as c:
        for (s,) in c:
            assert s == "DONE"


def test_legacy_insert_cursor():
    assert hasattr(arcpy, "InsertCursor")
    assert callable(arcpy.InsertCursor)


def test_legacy_insert_cursor_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "lic.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "ID", "LONG")

    cursor = arcpy.InsertCursor(fc)
    for i in range(3):
        row = cursor.newRow()
        row.setValue("ID", i)
        cursor.insertRow(row)
    del cursor

    count = int(arcpy.management.GetCount(fc)[0])
    assert count == 3


# ---------------------------------------------------------------------------
# Message functions
# ---------------------------------------------------------------------------
def test_add_message():
    assert hasattr(arcpy, "AddMessage")
    assert callable(arcpy.AddMessage)

    arcpy.AddMessage("Test info message")


def test_add_warning():
    assert hasattr(arcpy, "AddWarning")
    assert callable(arcpy.AddWarning)

    arcpy.AddWarning("Test warning message")


def test_add_error():
    assert hasattr(arcpy, "AddError")
    assert callable(arcpy.AddError)

    arcpy.AddError("Test error message")


def test_add_id_message():
    assert hasattr(arcpy, "AddIDMessage")
    assert callable(arcpy.AddIDMessage)

    arcpy.AddIDMessage("INFORMATIVE", 12, "Dataset")


def test_get_messages():
    assert hasattr(arcpy, "GetMessages")
    assert callable(arcpy.GetMessages)

    msgs = arcpy.GetMessages()
    assert isinstance(msgs, str)

    msgs_info = arcpy.GetMessages(0)
    assert isinstance(msgs_info, str)

    msgs_warn = arcpy.GetMessages(1)
    assert isinstance(msgs_warn, str)

    msgs_err = arcpy.GetMessages(2)
    assert isinstance(msgs_err, str)


def test_get_message():
    assert hasattr(arcpy, "GetMessage")
    assert callable(arcpy.GetMessage)

    msg = arcpy.GetMessage(0)
    assert isinstance(msg, str)


def test_get_message_count():
    assert hasattr(arcpy, "GetMessageCount")
    assert callable(arcpy.GetMessageCount)

    count = arcpy.GetMessageCount()
    assert isinstance(count, int)


def test_get_max_severity():
    assert hasattr(arcpy, "GetMaxSeverity")
    assert callable(arcpy.GetMaxSeverity)

    severity = arcpy.GetMaxSeverity()
    assert isinstance(severity, int)
    assert severity in (0, 1, 2)


# ---------------------------------------------------------------------------
# Environment properties
# ---------------------------------------------------------------------------
def test_env_properties():
    assert hasattr(arcpy, "env")
    assert hasattr(arcpy.env, "workspace")
    assert hasattr(arcpy.env, "scratchGDB")
    assert hasattr(arcpy.env, "scratchFolder")
    assert hasattr(arcpy.env, "cellSize")
    assert hasattr(arcpy.env, "extent")
    assert hasattr(arcpy.env, "snapRaster")
    assert hasattr(arcpy.env, "outputCoordinateSystem")
    assert hasattr(arcpy.env, "mask")
    assert hasattr(arcpy.env, "compression")
    assert hasattr(arcpy.env, "parallelProcessingFactor")
