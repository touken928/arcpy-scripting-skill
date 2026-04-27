"""Tests for arcpy.analysis module - all functions, parameters, and return values
documented in skills/arcpy-scripting/modules/arcpy-analysis.md"""

import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, create_point_fc, create_polygon_fc, new_file_gdb


# ---------------------------------------------------------------------------
# Buffer
# ---------------------------------------------------------------------------
def test_analysis_buffer_exists_and_callable():
    assert hasattr(arcpy.analysis, "Buffer")
    assert callable(arcpy.analysis.Buffer)


def test_analysis_buffer_parameters_distances(tmp_path):
    """Test Buffer with various distance specs and dissolve options."""
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "buf.gdb")[0]
    pts = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(pts, ["SHAPE@XY"]) as cursor:
        cursor.insertRow(((120.0, 30.0),))
        cursor.insertRow(((120.01, 30.0),))

    # String distance with dissolve
    r1 = arcpy.analysis.Buffer(pts, f"{gdb}/buf1", "100 Meters", dissolve_option="ALL")
    assert arcpy.Exists(r1[0])
    assert isinstance(r1, arcpy.Result)

    # Numeric distance
    r2 = arcpy.analysis.Buffer(pts, f"{gdb}/buf2", 200)
    assert arcpy.Exists(r2[0])

    # Field buffer (use VALUE field)
    arcpy.management.AddField(pts, "BUFF_DIST", "DOUBLE", field_length=10)
    arcpy.management.CalculateField(pts, "BUFF_DIST", "150", "PYTHON3")
    r3 = arcpy.analysis.Buffer(pts, f"{gdb}/buf3", "BUFF_DIST")
    assert arcpy.Exists(r3[0])


def test_analysis_buffer_line_side_parameters(tmp_path):
    """Test Buffer line_side parameter acceptance."""
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "bufs.gdb")[0]
    line = arcpy.management.CreateFeatureclass(gdb, "line", "POLYLINE", spatial_reference=4326)[0]
    arr = arcpy.Array([arcpy.Point(120.0, 30.0), arcpy.Point(120.02, 30.02)])
    with arcpy.da.InsertCursor(line, ["SHAPE@"]) as cursor:
        cursor.insertRow([arcpy.Polyline(arr, arcpy.SpatialReference(4326))])

    for side in ["FULL", "LEFT", "RIGHT"]:
        out = f"{gdb}/buf_{side}"
        r = arcpy.analysis.Buffer(line, out, "50 Meters", line_side=side)
        assert arcpy.Exists(r[0])

    for end_type in ["ROUND", "FLAT"]:
        out = f"{gdb}/buf_{end_type}"
        r = arcpy.analysis.Buffer(line, out, "50 Meters", line_end_type=end_type)
        assert arcpy.Exists(r[0])

    for method in ["PLANAR", "GEODESIC"]:
        out = f"{gdb}/buf_{method}"
        r = arcpy.analysis.Buffer(line, out, "50 Meters", method=method)
        assert arcpy.Exists(r[0])


def test_analysis_buffer_dissolve_options(tmp_path):
    """Test Buffer dissolve_option=NONE/ALL/LIST."""
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "bufd.gdb")[0]
    pts = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(pts, "CAT", "TEXT", field_length=10)
    with arcpy.da.InsertCursor(pts, ["SHAPE@XY", "CAT"]) as cursor:
        cursor.insertRow(((120.0, 30.0), "A"))
        cursor.insertRow(((120.01, 30.0), "B"))
        cursor.insertRow(((120.02, 30.0), "A"))

    for opt in ["NONE", "ALL", "LIST"]:
        out = f"{gdb}/buf_{opt}"
        kwargs = {"dissolve_option": opt}
        if opt == "LIST":
            kwargs["dissolve_field"] = "CAT"
        r = arcpy.analysis.Buffer(pts, out, "50 Meters", **kwargs)
        assert arcpy.Exists(r[0])


# ---------------------------------------------------------------------------
# Clip
# ---------------------------------------------------------------------------
def test_analysis_clip():
    assert hasattr(arcpy.analysis, "Clip")
    assert callable(arcpy.analysis.Clip)


def test_analysis_clip_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "clip.gdb")[0]
    pts = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(pts, ["SHAPE@XY"]) as cursor:
        cursor.insertRow(((120.0, 30.0),))
        cursor.insertRow(((120.02, 30.0),))

    # Create clip polygon that covers first point only
    arr = arcpy.Array([arcpy.Point(119.99, 29.99), arcpy.Point(120.01, 29.99),
                       arcpy.Point(120.01, 30.01), arcpy.Point(119.99, 30.01),
                       arcpy.Point(119.99, 29.99)])
    poly = arcpy.management.CreateFeatureclass(gdb, "clip_poly", "POLYGON", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(poly, ["SHAPE@"]) as cursor:
        cursor.insertRow([arcpy.Polygon(arr, arcpy.SpatialReference(4326))])

    r = arcpy.analysis.Clip(pts, poly, f"{gdb}/clipped")
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)
    count = int(arcpy.management.GetCount(r[0])[0])
    assert count == 1


def test_analysis_clip_with_cluster_tolerance(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "clipc.gdb")[0]
    pts = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(pts, ["SHAPE@XY"]) as cursor:
        cursor.insertRow(((120.0, 30.0),))
    poly = arcpy.management.CreateFeatureclass(gdb, "poly", "POLYGON", spatial_reference=4326)[0]
    arr = arcpy.Array([arcpy.Point(119.99, 29.99), arcpy.Point(120.01, 29.99),
                       arcpy.Point(120.01, 30.01), arcpy.Point(119.99, 30.01),
                       arcpy.Point(119.99, 29.99)])
    with arcpy.da.InsertCursor(poly, ["SHAPE@"]) as cursor:
        cursor.insertRow([arcpy.Polygon(arr, arcpy.SpatialReference(4326))])

    r = arcpy.analysis.Clip(pts, poly, f"{gdb}/clipped", cluster_tolerance="0.001 Meters")
    assert arcpy.Exists(r[0])


# ---------------------------------------------------------------------------
# Intersect
# ---------------------------------------------------------------------------
def test_analysis_intersect():
    assert hasattr(arcpy.analysis, "Intersect")
    assert callable(arcpy.analysis.Intersect)


def test_analysis_intersect_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "intx.gdb")[0]
    # Two overlapping polygons
    arr1 = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(10, 0), arcpy.Point(10, 10),
                        arcpy.Point(0, 10), arcpy.Point(0, 0)])
    arr2 = arcpy.Array([arcpy.Point(5, 5), arcpy.Point(15, 5), arcpy.Point(15, 15),
                        arcpy.Point(5, 15), arcpy.Point(5, 5)])
    sr = arcpy.SpatialReference(3857)
    p1 = arcpy.management.CreateFeatureclass(gdb, "poly1", "POLYGON", spatial_reference=sr)[0]
    p2 = arcpy.management.CreateFeatureclass(gdb, "poly2", "POLYGON", spatial_reference=sr)[0]
    with arcpy.da.InsertCursor(p1, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr1, sr)])
    with arcpy.da.InsertCursor(p2, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr2, sr)])

    for join_attr in ["ALL", "NO_FID", "ONLY_FID"]:
        out = f"{gdb}/int_{join_attr}"
        r = arcpy.analysis.Intersect([p1, p2], out, join_attributes=join_attr)
        assert arcpy.Exists(r[0])

    # With output_type
    r = arcpy.analysis.Intersect([p1, p2], f"{gdb}/int_point", output_type="POINT")
    assert arcpy.Exists(r[0])


# ---------------------------------------------------------------------------
# Union
# ---------------------------------------------------------------------------
def test_analysis_union():
    assert hasattr(arcpy.analysis, "Union")
    assert callable(arcpy.analysis.Union)


def test_analysis_union_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "union.gdb")[0]
    sr = arcpy.SpatialReference(3857)
    arr1 = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(10, 0), arcpy.Point(10, 10),
                        arcpy.Point(0, 10), arcpy.Point(0, 0)])
    arr2 = arcpy.Array([arcpy.Point(5, 0), arcpy.Point(15, 0), arcpy.Point(15, 10),
                        arcpy.Point(5, 10), arcpy.Point(5, 0)])
    p1 = arcpy.management.CreateFeatureclass(gdb, "p1", "POLYGON", spatial_reference=sr)[0]
    p2 = arcpy.management.CreateFeatureclass(gdb, "p2", "POLYGON", spatial_reference=sr)[0]
    with arcpy.da.InsertCursor(p1, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr1, sr)])
    with arcpy.da.InsertCursor(p2, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr2, sr)])

    for gaps in ["GAPS", "NO_GAPS"]:
        out = f"{gdb}/union_{gaps}"
        r = arcpy.analysis.Union([p1, p2], out, gaps=gaps)
        assert arcpy.Exists(r[0])
        assert isinstance(r, arcpy.Result)


# ---------------------------------------------------------------------------
# Erase
# ---------------------------------------------------------------------------
def test_analysis_erase():
    assert hasattr(arcpy.analysis, "Erase")
    assert callable(arcpy.analysis.Erase)


def test_analysis_erase_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "erase.gdb")[0]
    sr = arcpy.SpatialReference(3857)
    arr_p = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(20, 0), arcpy.Point(20, 20),
                         arcpy.Point(0, 20), arcpy.Point(0, 0)])
    arr_e = arcpy.Array([arcpy.Point(5, 5), arcpy.Point(15, 5), arcpy.Point(15, 15),
                         arcpy.Point(5, 15), arcpy.Point(5, 5)])
    p = arcpy.management.CreateFeatureclass(gdb, "in_poly", "POLYGON", spatial_reference=sr)[0]
    e = arcpy.management.CreateFeatureclass(gdb, "erase_poly", "POLYGON", spatial_reference=sr)[0]
    with arcpy.da.InsertCursor(p, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr_p, sr)])
    with arcpy.da.InsertCursor(e, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr_e, sr)])

    r = arcpy.analysis.Erase(p, e, f"{gdb}/erased")
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------
def test_analysis_identity():
    assert hasattr(arcpy.analysis, "Identity")
    assert callable(arcpy.analysis.Identity)


def test_analysis_identity_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "ident.gdb")[0]
    sr = arcpy.SpatialReference(3857)
    arr1 = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(10, 0), arcpy.Point(10, 10),
                        arcpy.Point(0, 10), arcpy.Point(0, 0)])
    arr2 = arcpy.Array([arcpy.Point(3, 3), arcpy.Point(7, 3), arcpy.Point(7, 7),
                        arcpy.Point(3, 7), arcpy.Point(3, 3)])
    p1 = arcpy.management.CreateFeatureclass(gdb, "in_poly", "POLYGON", spatial_reference=sr)[0]
    p2 = arcpy.management.CreateFeatureclass(gdb, "ident_poly", "POLYGON", spatial_reference=sr)[0]
    with arcpy.da.InsertCursor(p1, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr1, sr)])
    with arcpy.da.InsertCursor(p2, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr2, sr)])

    for join_attr in ["ALL", "NO_FID", "ONLY_FID"]:
        out = f"{gdb}/ident_{join_attr}"
        r = arcpy.analysis.Identity(p1, p2, out, join_attributes=join_attr)
        assert arcpy.Exists(r[0])
        assert r[0] is not None


# ---------------------------------------------------------------------------
# SpatialJoin
# ---------------------------------------------------------------------------
def test_analysis_spatial_join():
    assert hasattr(arcpy.analysis, "SpatialJoin")
    assert callable(arcpy.analysis.SpatialJoin)


def test_analysis_spatial_join_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "sj.gdb")[0]
    pts = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(pts, "NAME", "TEXT", field_length=20)
    with arcpy.da.InsertCursor(pts, ["SHAPE@XY", "NAME"]) as c:
        c.insertRow(((120.0, 30.0), "Site A"))
        c.insertRow(((120.05, 30.05), "Site B"))

    poly = arcpy.management.CreateFeatureclass(gdb, "poly", "POLYGON", spatial_reference=4326)[0]
    arcpy.management.AddField(poly, "ZONE", "TEXT", field_length=10)
    arr = arcpy.Array([arcpy.Point(119.99, 29.99), arcpy.Point(120.03, 29.99),
                       arcpy.Point(120.03, 30.03), arcpy.Point(119.99, 30.03),
                       arcpy.Point(119.99, 29.99)])
    with arcpy.da.InsertCursor(poly, ["SHAPE@", "ZONE"]) as c:
        c.insertRow([arcpy.Polygon(arr, arcpy.SpatialReference(4326)), "Zone 1"])

    for join_op in ["JOIN_ONE_TO_ONE", "JOIN_ONE_TO_MANY"]:
        out = f"{gdb}/sj_{join_op}"
        r = arcpy.analysis.SpatialJoin(pts, poly, out, join_operation=join_op,
                                        join_type="KEEP_ALL", match_option="INTERSECT")
        assert arcpy.Exists(r[0])

    for match in ["INTERSECT", "WITHIN", "CONTAINS", "COMPLETELY_CONTAINS",
                  "CROSSES", "ARE_IDENTICAL_TO", "BOUNDARY_TOUCHES"]:
        out = f"{gdb}/sj_m_{match}"
        try:
            r = arcpy.analysis.SpatialJoin(pts, poly, out, match_option=match)
            assert arcpy.Exists(r[0])
        except Exception:
            pass

    # With search_radius
    out = f"{gdb}/sj_radius"
    r = arcpy.analysis.SpatialJoin(pts, poly, out, match_option="WITHIN_A_DISTANCE",
                                    search_radius="500 Meters")
    assert arcpy.Exists(r[0])

    # With distance_field_name
    out = f"{gdb}/sj_distfield"
    r = arcpy.analysis.SpatialJoin(pts, poly, out, match_option="WITHIN_A_DISTANCE",
                                    search_radius="500 Meters", distance_field_name="DIST_KM")
    assert arcpy.Exists(r[0])

    # Test join_type=KEEP_COMMON
    out = f"{gdb}/sj_common"
    r = arcpy.analysis.SpatialJoin(pts, poly, out, join_type="KEEP_COMMON", match_option="INTERSECT")
    assert arcpy.Exists(r[0])


# ---------------------------------------------------------------------------
# Near
# ---------------------------------------------------------------------------
def test_analysis_near():
    assert hasattr(arcpy.analysis, "Near")
    assert callable(arcpy.analysis.Near)


def test_analysis_near_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "near.gdb")[0]
    pts1 = arcpy.management.CreateFeatureclass(gdb, "pts1", "POINT", spatial_reference=4326)[0]
    pts2 = arcpy.management.CreateFeatureclass(gdb, "pts2", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(pts1, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))
        c.insertRow(((120.5, 30.5),))
    with arcpy.da.InsertCursor(pts2, ["SHAPE@XY"]) as c:
        c.insertRow(((120.01, 30.01),))
        c.insertRow(((120.51, 30.51),))

    # Basic Near
    r = arcpy.analysis.Near(pts1, pts2)
    assert isinstance(r, arcpy.Result)

    # Near with search_radius
    r = arcpy.analysis.Near(pts1, pts2, search_radius="5 Kilometers")
    assert isinstance(r, arcpy.Result)

    # Near with location and angle
    r = arcpy.analysis.Near(pts1, pts2, search_radius="2000 Meters",
                             location="LOCATION", angle="ANGLE")
    assert isinstance(r, arcpy.Result)

    # Near with method
    for method in ["PLANAR", "GEODESIC"]:
        r = arcpy.analysis.Near(pts1, pts2, search_radius="2000 Meters", method=method)
        assert isinstance(r, arcpy.Result)

    # Verify NEAR_FID and NEAR_DIST fields exist
    fields = [f.name for f in arcpy.ListFields(pts1)]
    assert "NEAR_FID" in fields
    assert "NEAR_DIST" in fields


# ---------------------------------------------------------------------------
# GenerateNearTable
# ---------------------------------------------------------------------------
def test_analysis_generate_near_table():
    assert hasattr(arcpy.analysis, "GenerateNearTable")
    assert callable(arcpy.analysis.GenerateNearTable)


def test_analysis_generate_near_table_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "gnt.gdb")[0]
    pts1 = arcpy.management.CreateFeatureclass(gdb, "pts1", "POINT", spatial_reference=4326)[0]
    pts2 = arcpy.management.CreateFeatureclass(gdb, "pts2", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(pts1, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))
        c.insertRow(((120.5, 30.5),))
    with arcpy.da.InsertCursor(pts2, ["SHAPE@XY"]) as c:
        c.insertRow(((120.01, 30.01),))

    for closest in ["1", "ALL"]:
        out = f"{gdb}/nt_{closest}"
        r = arcpy.analysis.GenerateNearTable(pts1, pts2, out,
                                              search_radius="1 Kilometers",
                                              closest=closest)
        assert arcpy.Exists(r[0])
        assert isinstance(r, arcpy.Result)

    for method in ["PLANAR", "GEODESIC"]:
        out = f"{gdb}/nt_m_{method}"
        r = arcpy.analysis.GenerateNearTable(pts1, pts2, out, method=method)
        assert arcpy.Exists(r[0])


# ---------------------------------------------------------------------------
# PointDistance
# ---------------------------------------------------------------------------
def test_analysis_point_distance():
    assert hasattr(arcpy.analysis, "PointDistance")
    assert callable(arcpy.analysis.PointDistance)


def test_analysis_point_distance_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "pdist.gdb")[0]
    pts1 = arcpy.management.CreateFeatureclass(gdb, "src", "POINT", spatial_reference=4326)[0]
    pts2 = arcpy.management.CreateFeatureclass(gdb, "near", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(pts1, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))
    with arcpy.da.InsertCursor(pts2, ["SHAPE@XY"]) as c:
        c.insertRow(((120.01, 30.01),))

    r = arcpy.analysis.PointDistance(pts1, pts2, f"{gdb}/pd_table")
    assert arcpy.Exists(r[0])

    r2 = arcpy.analysis.PointDistance(pts1, pts2, f"{gdb}/pd_table2",
                                       search_radius="5 Kilometers")
    assert arcpy.Exists(r2[0])


# ---------------------------------------------------------------------------
# SelectLayerByLocation
# ---------------------------------------------------------------------------
def test_analysis_select_layer_by_location():
    assert hasattr(arcpy.management, "SelectLayerByLocation")
    assert callable(arcpy.management.SelectLayerByLocation)


def test_analysis_select_layer_by_location_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "selloc.gdb")[0]
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
    for overlap in ["INTERSECT", "WITHIN_A_DISTANCE"]:
        kwargs = {}
        if overlap == "WITHIN_A_DISTANCE":
            kwargs["search_distance"] = "100 Meters"
        r = arcpy.management.SelectLayerByLocation(lyr, overlap, poly, **kwargs)
        assert isinstance(r, arcpy.Result)

    for sel_type in ["NEW_SELECTION", "ADD_TO_SELECTION", "REMOVE_FROM_SELECTION",
                      "SUBSET_SELECTION", "SWITCH_SELECTION"]:
        r = arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", poly, selection_type=sel_type)
        assert isinstance(r, arcpy.Result)

    for invert in ["INVERT", "NOT_INVERT"]:
        r = arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", poly, None, "NEW_SELECTION", invert)
        assert isinstance(r, arcpy.Result)


# ---------------------------------------------------------------------------
# Dissolve
# ---------------------------------------------------------------------------
def test_analysis_dissolve():
    assert hasattr(arcpy.management, "Dissolve")
    assert callable(arcpy.management.Dissolve)


def test_analysis_dissolve_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "diss.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "fc", "POLYGON", spatial_reference=3857)[0]
    arcpy.management.AddField(fc, "ZONE_CODE", "TEXT", field_length=10)
    arcpy.management.AddField(fc, "AREA", "DOUBLE")

    sr = arcpy.SpatialReference(3857)
    arr1 = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(10, 0), arcpy.Point(10, 10),
                        arcpy.Point(0, 10), arcpy.Point(0, 0)])
    arr2 = arcpy.Array([arcpy.Point(10, 0), arcpy.Point(20, 0), arcpy.Point(20, 10),
                        arcpy.Point(10, 10), arcpy.Point(10, 0)])
    with arcpy.da.InsertCursor(fc, ["SHAPE@", "ZONE_CODE", "AREA"]) as c:
        c.insertRow([arcpy.Polygon(arr1, sr), "A", 100.0])
        c.insertRow([arcpy.Polygon(arr2, sr), "A", 200.0])

    # Basic dissolve
    r = arcpy.management.Dissolve(fc, f"{gdb}/diss1", dissolve_field="ZONE_CODE")
    assert arcpy.Exists(r[0])

    # With statistics_fields
    r = arcpy.management.Dissolve(fc, f"{gdb}/diss2", dissolve_field="ZONE_CODE",
                                 statistics_fields="AREA SUM")
    assert arcpy.Exists(r[0])

    # With multi_part
    for mp in ["MULTI_PART", "SINGLE_PART"]:
        out = f"{gdb}/diss_{mp}"
        r = arcpy.management.Dissolve(fc, out, dissolve_field="ZONE_CODE", multi_part=mp)
        assert arcpy.Exists(r[0])


# ---------------------------------------------------------------------------
# FeatureToPoint
# ---------------------------------------------------------------------------
def test_analysis_feature_to_point():
    assert hasattr(arcpy.management, "FeatureToPoint")
    assert callable(arcpy.management.FeatureToPoint)


def test_analysis_feature_to_point_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "ftp.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "poly", "POLYGON", spatial_reference=3857)[0]
    sr = arcpy.SpatialReference(3857)
    arr = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(10, 0), arcpy.Point(10, 10),
                       arcpy.Point(0, 10), arcpy.Point(0, 0)])
    with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polygon(arr, sr)])

    for loc in ["CENTROID", "INSIDE"]:
        out = f"{gdb}/pt_{loc}"
        r = arcpy.management.FeatureToPoint(fc, out, point_location=loc)
        assert arcpy.Exists(r[0])

    geom_type = arcpy.Describe(f"{gdb}/pt_CENTROID").shapeType
    assert geom_type == "Point"


# ---------------------------------------------------------------------------
# FeatureToLine
# ---------------------------------------------------------------------------
def test_analysis_feature_to_line():
    assert hasattr(arcpy.management, "FeatureToLine")
    assert callable(arcpy.management.FeatureToLine)


def test_analysis_feature_to_line_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "ftl.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "lines", "POLYLINE", spatial_reference=3857)[0]
    arcpy.management.AddField(fc, "ZONE_ID", "TEXT", field_length=10)
    sr = arcpy.SpatialReference(3857)
    arr1 = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(5, 5)])
    arr2 = arcpy.Array([arcpy.Point(5, 5), arcpy.Point(10, 0)])
    with arcpy.da.InsertCursor(fc, ["SHAPE@", "ZONE_ID"]) as c:
        c.insertRow([arcpy.Polyline(arr1, sr), "A"])
        c.insertRow([arcpy.Polyline(arr2, sr), "B"])

    r = arcpy.management.FeatureToLine(fc, f"{gdb}/merged_line")
    assert arcpy.Exists(r[0])

    r2 = arcpy.management.FeatureToLine(fc, f"{gdb}/split_line", attributes="ATTRIBUTES")
    assert arcpy.Exists(r2[0])


# ---------------------------------------------------------------------------
# MultipartToSinglepart
# ---------------------------------------------------------------------------
def test_analysis_multipart_to_singlepart():
    assert hasattr(arcpy.management, "MultipartToSinglepart")
    assert callable(arcpy.management.MultipartToSinglepart)


def test_analysis_multipart_to_singlepart_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "mtsp.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "multi", "POLYGON", spatial_reference=3857)[0]
    sr = arcpy.SpatialReference(3857)
    # Create a multipart polygon
    arr1 = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(5, 0), arcpy.Point(5, 5),
                        arcpy.Point(0, 5), arcpy.Point(0, 0)])
    arr2 = arcpy.Array([arcpy.Point(10, 10), arcpy.Point(15, 10), arcpy.Point(15, 15),
                        arcpy.Point(10, 15), arcpy.Point(10, 10)])
    pg = arcpy.Polygon(arcpy.Array([arr1, arr2]), sr)
    with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as c:
        c.insertRow([pg])

    r = arcpy.management.MultipartToSinglepart(fc, f"{gdb}/single")
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)
    # Should have 2 features now
    count = int(arcpy.management.GetCount(r[0])[0])
    assert count == 2


# ---------------------------------------------------------------------------
# Eliminate
# ---------------------------------------------------------------------------
def test_analysis_eliminate():
    assert hasattr(arcpy.management, "Eliminate")
    assert callable(arcpy.management.Eliminate)


def test_analysis_eliminate_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "elim.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "polys", "POLYGON", spatial_reference=3857)[0]
    arcpy.management.AddField(fc, "AREA", "DOUBLE")
    sr = arcpy.SpatialReference(3857)
    arr1 = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(10, 0), arcpy.Point(10, 10),
                        arcpy.Point(0, 10), arcpy.Point(0, 0)])
    arr2 = arcpy.Array([arcpy.Point(10, 0), arcpy.Point(11, 0), arcpy.Point(11, 10),
                        arcpy.Point(10, 10), arcpy.Point(10, 0)])
    with arcpy.da.InsertCursor(fc, ["SHAPE@", "AREA"]) as c:
        c.insertRow([arcpy.Polygon(arr1, sr), 100.0])
        c.insertRow([arcpy.Polygon(arr2, sr), 1.0])

    lyr = arcpy.management.MakeFeatureLayer(fc, "elim_lyr", "AREA < 10")[0]
    r = arcpy.management.Eliminate(lyr, f"{gdb}/elim1")
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)
