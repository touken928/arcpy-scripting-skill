"""Tests for arcpy.conversion module - all functions, parameters, and return values
documented in skills/arcpy-scripting/modules/arcpy-conversion.md"""

import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, create_point_fc, create_polygon_fc, new_file_gdb


# ---------------------------------------------------------------------------
# FeatureClassToFeatureClass
# ---------------------------------------------------------------------------
def test_conversion_fc_to_fc_exists():
    assert hasattr(arcpy.conversion, "FeatureClassToFeatureClass")
    assert callable(arcpy.conversion.FeatureClassToFeatureClass)


def test_conversion_fc_to_fc_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "conv.gdb")[0]
    pts = arcpy.management.CreateFeatureclass(gdb, "src", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(pts, "ROAD_CLASS", "TEXT", field_length=5)
    arcpy.management.AddField(pts, "NAME", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(pts, ["SHAPE@XY", "ROAD_CLASS", "NAME"]) as c:
        c.insertRow(((120.0, 30.0), "A", "站点1"))
        c.insertRow(((121.0, 31.0), "B", "站点2"))
        c.insertRow(((122.0, 32.0), "A", "站点3"))

    # Basic conversion
    r = arcpy.conversion.FeatureClassToFeatureClass(pts, gdb, "pts_a")
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)
    count = int(arcpy.management.GetCount(r[0])[0])
    assert count == 3

    # With where_clause
    r = arcpy.conversion.FeatureClassToFeatureClass(pts, gdb, "pts_filtered",
                                                      where_clause="ROAD_CLASS = 'A'")
    assert arcpy.Exists(r[0])
    count = int(arcpy.management.GetCount(r[0])[0])
    assert count == 2

    # With field_mapping
    r = arcpy.conversion.FeatureClassToFeatureClass(
        pts, gdb, "pts_mapped",
        where_clause="ROAD_CLASS = 'A'",
        field_mapping='NAME "名称" true true false 50 Text 0 0,First,#,src,NAME,-1,-1'
    )
    assert arcpy.Exists(r[0])

    # With config_keyword
    r = arcpy.conversion.FeatureClassToFeatureClass(pts, gdb, "pts_cfg",
                                                      config_keyword="DEFAULTS")
    assert arcpy.Exists(r[0])


# ---------------------------------------------------------------------------
# TableToTable
# ---------------------------------------------------------------------------
def test_conversion_table_to_table():
    assert hasattr(arcpy.conversion, "TableToTable")
    assert callable(arcpy.conversion.TableToTable)


def test_conversion_table_to_table_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "tbl.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "fc", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "CATEGORY", "TEXT", field_length=10)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "CATEGORY"]) as c:
        c.insertRow(((120.0, 30.0), "TYPE_A"))
        c.insertRow(((121.0, 31.0), "TYPE_B"))

    r = arcpy.conversion.TableToTable(fc, gdb, "poi_tbl")
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)

    r2 = arcpy.conversion.TableToTable(fc, gdb, "poi_filtered",
                                        where_clause="CATEGORY = 'TYPE_A'")
    assert arcpy.Exists(r2[0])


# ---------------------------------------------------------------------------
# ExportFeatures
# ---------------------------------------------------------------------------
def test_conversion_export_features():
    assert hasattr(arcpy.conversion, "ExportFeatures")
    assert callable(arcpy.conversion.ExportFeatures)


def test_conversion_export_features_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "expf.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "src", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "NAME", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "NAME"]) as c:
        c.insertRow(((120.0, 30.0), "B"))
        c.insertRow(((121.0, 31.0), "A"))
        c.insertRow(((122.0, 32.0), "C"))

    r = arcpy.conversion.ExportFeatures(fc, f"{gdb}/exported")
    assert arcpy.Exists(r[0])

    r2 = arcpy.conversion.ExportFeatures(fc, f"{gdb}/exported_sort", sort_field="NAME A")
    assert arcpy.Exists(r2[0])

    r3 = arcpy.conversion.ExportFeatures(fc, f"{gdb}/exported_filter",
                                          where_clause="NAME = 'A'")
    assert arcpy.Exists(r3[0])

    r4 = arcpy.conversion.ExportFeatures(fc, f"{gdb}/exported_alias",
                                          use_field_alias_as_name="USE_ALIAS")
    assert arcpy.Exists(r4[0])


# ---------------------------------------------------------------------------
# ExportRaster
# ---------------------------------------------------------------------------
def test_conversion_export_raster():
    assert hasattr(arcpy.conversion, "ExportRaster")
    assert callable(arcpy.conversion.ExportRaster)


def test_conversion_export_raster_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "expr.gdb")[0]
    # Create a simple constant raster
    out_raster = arcpy.sa.CreateConstantRaster(1, "INTEGER", 10, arcpy.Extent(0, 0, 100, 100))
    raster_path = f"{gdb}/const_ras"
    out_raster.save(raster_path)

    r = arcpy.conversion.ExportRaster(raster_path, f"{gdb}/exported_ras")
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)


# ---------------------------------------------------------------------------
# FeatureToPoint
# ---------------------------------------------------------------------------
def test_conversion_feature_to_point():
    assert hasattr(arcpy.conversion, "FeatureToPoint")
    assert callable(arcpy.conversion.FeatureToPoint)


def test_conversion_feature_to_point_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "cftp.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "poly", "POLYGON", spatial_reference=3857)[0]
    sr = arcpy.SpatialReference(3857)
    arr = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(10, 0), arcpy.Point(10, 10),
                       arcpy.Point(0, 10), arcpy.Point(0, 0)])
    with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr, sr)])

    for loc in ["CENTROID", "INSIDE"]:
        out = f"{gdb}/cpt_{loc}"
        r = arcpy.conversion.FeatureToPoint(fc, out, point_location=loc)
        assert arcpy.Exists(r[0])
        assert r[0] is not None


# ---------------------------------------------------------------------------
# FeatureToLine
# ---------------------------------------------------------------------------
def test_conversion_feature_to_line():
    assert hasattr(arcpy.conversion, "FeatureToLine")
    assert callable(arcpy.conversion.FeatureToLine)


def test_conversion_feature_to_line_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "cftl.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "lines", "POLYLINE", spatial_reference=3857)[0]
    arcpy.management.AddField(fc, "ZONE_ID", "TEXT", field_length=10)
    sr = arcpy.SpatialReference(3857)
    arr1 = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(5, 5)])
    arr2 = arcpy.Array([arcpy.Point(5, 5), arcpy.Point(10, 0)])
    with arcpy.da.InsertCursor(fc, ["SHAPE@", "ZONE_ID"]) as c:
        c.insertRow([arcpy.Polyline(arr1, sr), "A"])
        c.insertRow([arcpy.Polyline(arr2, sr), "B"])

    r = arcpy.conversion.FeatureToLine(fc, f"{gdb}/merged")
    assert arcpy.Exists(r[0])

    r2 = arcpy.conversion.FeatureToLine(fc, f"{gdb}/split", line_field="ZONE_ID")
    assert arcpy.Exists(r2[0])


# ---------------------------------------------------------------------------
# FeatureToPolygon
# ---------------------------------------------------------------------------
def test_conversion_feature_to_polygon():
    assert hasattr(arcpy.conversion, "FeatureToPolygon")
    assert callable(arcpy.conversion.FeatureToPolygon)


def test_conversion_feature_to_polygon_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "cftpoly.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "lines", "POLYLINE", spatial_reference=3857)[0]
    sr = arcpy.SpatialReference(3857)
    # Closed line forming a polygon
    arr = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(10, 0), arcpy.Point(10, 10),
                       arcpy.Point(0, 10), arcpy.Point(0, 0)])
    with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polyline(arr, sr)])

    r = arcpy.conversion.FeatureToPolygon(fc, f"{gdb}/poly")
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)


# ---------------------------------------------------------------------------
# RasterToPolygon
# ---------------------------------------------------------------------------
def test_conversion_raster_to_polygon():
    assert hasattr(arcpy.conversion, "RasterToPolygon")
    assert callable(arcpy.conversion.RasterToPolygon)


def test_conversion_raster_to_polygon_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "rtpoly.gdb")[0]
    out_raster = arcpy.sa.CreateConstantRaster(1, "INTEGER", 10, arcpy.Extent(0, 0, 100, 100))
    raster_path = f"{gdb}/const_ras"
    out_raster.save(raster_path)

    for simplify in ["SIMPLIFY", "NO_SIMPLIFY"]:
        out = f"{gdb}/rtp_{simplify}"
        r = arcpy.conversion.RasterToPolygon(raster_path, out, simplify=simplify)
        assert arcpy.Exists(r[0])

    for mp in ["MULTIPLE_PART", "SINGLE_PART"]:
        out = f"{gdb}/rtp_{mp}"
        r = arcpy.conversion.RasterToPolygon(raster_path, out,
                                              create_multipart_features=mp)
        assert arcpy.Exists(r[0])

    r = arcpy.conversion.RasterToPolygon(raster_path, f"{gdb}/rtp_field",
                                          raster_field="Value",
                                          max_vertices_per_feature=500)
    assert arcpy.Exists(r[0])


# ---------------------------------------------------------------------------
# PolygonToRaster
# ---------------------------------------------------------------------------
def test_conversion_polygon_to_raster():
    assert hasattr(arcpy.conversion, "PolygonToRaster")
    assert callable(arcpy.conversion.PolygonToRaster)


def test_conversion_polygon_to_raster_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "ptor.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "zone", "POLYGON", spatial_reference=3857)[0]
    arcpy.management.AddField(fc, "ZONE_CODE", "SHORT")
    sr = arcpy.SpatialReference(3857)
    arr = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(100, 0), arcpy.Point(100, 100),
                       arcpy.Point(0, 100), arcpy.Point(0, 0)])
    with arcpy.da.InsertCursor(fc, ["SHAPE@", "ZONE_CODE"]) as c:
        c.insertRow([arcpy.Polygon(arr, sr), 1])

    r = arcpy.conversion.PolygonToRaster(fc, "ZONE_CODE", f"{gdb}/zone_ras", cellsize=10)
    assert arcpy.Exists(r[0])

    for ca in ["CELL_CENTER", "MAX_AREA", "MAX_COMBINED_AREA"]:
        out = f"{gdb}/zone_{ca}"
        r = arcpy.conversion.PolygonToRaster(fc, "ZONE_CODE", out, cellsize=10,
                                              cell_assignment=ca)
        assert arcpy.Exists(r[0])

    for rat in ["BUILD_RAT", "NO_BUILD_RAT"]:
        out = f"{gdb}/zone_{rat}"
        r = arcpy.conversion.PolygonToRaster(fc, "ZONE_CODE", out, cellsize=10,
                                              build_rat=rat)
        assert arcpy.Exists(r[0])

    r = arcpy.conversion.PolygonToRaster(fc, "ZONE_CODE", f"{gdb}/zone_prio",
                                          cellsize=10, priority_field="ZONE_CODE")
    assert arcpy.Exists(r[0])


# ---------------------------------------------------------------------------
# RasterToOtherFormat
# ---------------------------------------------------------------------------
def test_conversion_raster_to_other_format():
    assert hasattr(arcpy.conversion, "RasterToOtherFormat")
    assert callable(arcpy.conversion.RasterToOtherFormat)


def test_conversion_raster_to_other_format_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "rtof.gdb")[0]
    out_raster = arcpy.sa.CreateConstantRaster(1, "INTEGER", 10, arcpy.Extent(0, 0, 100, 100))
    raster_path = f"{gdb}/const_ras"
    out_raster.save(raster_path)

    out_dir = tmp_path / "out_images"
    out_dir.mkdir(parents=True, exist_ok=True)
    r = arcpy.conversion.RasterToOtherFormat(raster_path, str(out_dir), "TIFF",
                                              compression="LZW")
    assert isinstance(r, arcpy.Result)

    r2 = arcpy.conversion.RasterToOtherFormat(raster_path, str(out_dir), "JPEG",
                                               jpeg_quality=90)
    assert isinstance(r2, arcpy.Result)


# ---------------------------------------------------------------------------
# ShapefileToFeatureClass
# ---------------------------------------------------------------------------
def test_conversion_shapefile_to_fc():
    assert hasattr(arcpy.conversion, "ShapefileToFeatureClass")
    assert callable(arcpy.conversion.ShapefileToFeatureClass)


def test_conversion_shapefile_to_fc_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "shpfc.gdb")[0]
    # Create a shapefile via CopyFeatures to a folder
    shp_folder = tmp_path / "shp"
    shp_folder.mkdir(parents=True, exist_ok=True)
    fc = arcpy.management.CreateFeatureclass(gdb, "src", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))
    arcpy.management.CopyFeatures(fc, str(shp_folder / "src.shp"))

    r = arcpy.conversion.ShapefileToFeatureClass(str(shp_folder / "src.shp"), gdb, "imported")
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)


# ---------------------------------------------------------------------------
# JSONToFeatureClass / FeatureClassToJSON
# ---------------------------------------------------------------------------
def test_conversion_json_to_fc():
    assert hasattr(arcpy.conversion, "JSONToFeatureClass")
    assert callable(arcpy.conversion.JSONToFeatureClass)
    assert hasattr(arcpy.conversion, "FeatureClassToJSON")
    assert callable(arcpy.conversion.FeatureClassToJSON)


def test_conversion_json_roundtrip_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "json.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "src", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))

    json_path = tmp_path / "exported.json"
    r1 = arcpy.conversion.FeatureClassToJSON(fc, str(json_path), geoJSON="GEOJSON")
    assert json_path.exists()

    r2 = arcpy.conversion.JSONToFeatureClass(str(json_path), f"{gdb}/from_json",
                                              spatial_reference=4326)
    assert arcpy.Exists(r2[0])

    # Test include_fields parameter
    json_path2 = tmp_path / "exported2.json"
    r3 = arcpy.conversion.FeatureClassToJSON(fc, str(json_path2),
                                              include_fields="FID;Shape")
    assert json_path2.exists()


# ---------------------------------------------------------------------------
# GeoJSONToFeatures / FeaturesToGeoJSON
# ---------------------------------------------------------------------------
def test_conversion_geojson():
    assert hasattr(arcpy.conversion, "GeoJSONToFeatures")
    assert callable(arcpy.conversion.GeoJSONToFeatures)
    assert hasattr(arcpy.conversion, "FeaturesToGeoJSON")
    assert callable(arcpy.conversion.FeaturesToGeoJSON)


def test_conversion_geojson_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "geoj.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "src", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))

    json_path = tmp_path / "exported.geojson"
    r1 = arcpy.conversion.FeaturesToGeoJSON(fc, str(json_path))
    assert json_path.exists()
    assert isinstance(r1, arcpy.Result)

    r2 = arcpy.conversion.GeoJSONToFeatures(str(json_path), f"{gdb}/from_geojson",
                                             geometry_type="POINT")
    assert arcpy.Exists(r2[0])


# ---------------------------------------------------------------------------
# ValidateDataset
# ---------------------------------------------------------------------------
def test_conversion_validate_dataset():
    assert hasattr(arcpy.conversion, "ValidateDataset")
    assert callable(arcpy.conversion.ValidateDataset)


def test_conversion_validate_dataset_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "vds.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "valid_fc", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))

    r = arcpy.conversion.ValidateDataset(fc)
    assert isinstance(r, arcpy.Result)
    assert r[0] is not None  # Boolean (str)

    r2 = arcpy.conversion.ValidateDataset(fc, in_tolerance_value="0.001 Meters")
    assert isinstance(r2, arcpy.Result)
