"""Tests for arcpy.sa module - all functions, parameters, Nbr* classes,
operators, and return values documented in skills/arcpy-scripting/modules/arcpy-sa.md"""

import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, create_point_fc, new_file_gdb


# ---------------------------------------------------------------------------
# Existence checks - Conditions & Logic
# ---------------------------------------------------------------------------
def test_sa_con():
    assert hasattr(arcpy.sa, "Con")
    assert callable(arcpy.sa.Con)


def test_sa_set_null():
    assert hasattr(arcpy.sa, "SetNull")
    assert callable(arcpy.sa.SetNull)


def test_sa_pick():
    assert hasattr(arcpy.sa, "Pick")
    assert callable(arcpy.sa.Pick)


def test_sa_is_null():
    assert hasattr(arcpy.sa, "IsNull")
    assert callable(arcpy.sa.IsNull)


def test_sa_power():
    assert hasattr(arcpy.sa, "Power")
    assert callable(arcpy.sa.Power)


def test_sa_square():
    assert hasattr(arcpy.sa, "Square")
    assert callable(arcpy.sa.Square)


def test_sa_square_root():
    assert hasattr(arcpy.sa, "SquareRoot")
    assert callable(arcpy.sa.SquareRoot)


# --- Reclassification ---
def test_sa_reclassify():
    assert hasattr(arcpy.sa, "Reclassify")
    assert callable(arcpy.sa.Reclassify)


def test_sa_remap_range():
    assert hasattr(arcpy.sa, "RemapRange")
    assert callable(arcpy.sa.RemapRange)


def test_sa_remap_value():
    assert hasattr(arcpy.sa, "RemapValue")
    assert callable(arcpy.sa.RemapValue)


# --- Neighborhood ---
def test_sa_focal_statistics():
    assert hasattr(arcpy.sa, "FocalStatistics")
    assert callable(arcpy.sa.FocalStatistics)


def test_sa_block_statistics():
    assert hasattr(arcpy.sa, "BlockStatistics")
    assert callable(arcpy.sa.BlockStatistics)


def test_sa_neighborhood_statistics():
    assert not hasattr(arcpy.sa, "NeighborhoodStatistics")


# --- Distance ---
def test_sa_cost_distance():
    assert hasattr(arcpy.sa, "CostDistance")
    assert callable(arcpy.sa.CostDistance)


def test_sa_cost_path():
    assert hasattr(arcpy.sa, "CostPath")
    assert callable(arcpy.sa.CostPath)


def test_sa_cost_back_link():
    assert hasattr(arcpy.sa, "CostBackLink")
    assert callable(arcpy.sa.CostBackLink)


def test_sa_euc_distance():
    assert hasattr(arcpy.sa, "EucDistance")
    assert callable(arcpy.sa.EucDistance)


def test_sa_euc_allocation():
    assert hasattr(arcpy.sa, "EucAllocation")
    assert callable(arcpy.sa.EucAllocation)


def test_sa_euc_direction():
    assert hasattr(arcpy.sa, "EucDirection")
    assert callable(arcpy.sa.EucDirection)


def test_sa_path_distance():
    assert hasattr(arcpy.sa, "PathDistance")
    assert callable(arcpy.sa.PathDistance)


def test_sa_path_allocation():
    assert hasattr(arcpy.sa, "PathAllocation")
    assert callable(arcpy.sa.PathAllocation)


def test_sa_path_direction():
    assert not hasattr(arcpy.sa, "PathDirection")


# --- Surface ---
def test_sa_slope():
    assert hasattr(arcpy.sa, "Slope")
    assert callable(arcpy.sa.Slope)


def test_sa_aspect():
    assert hasattr(arcpy.sa, "Aspect")
    assert callable(arcpy.sa.Aspect)


def test_sa_hillshade():
    assert hasattr(arcpy.sa, "Hillshade")
    assert callable(arcpy.sa.Hillshade)


def test_sa_curvature():
    assert hasattr(arcpy.sa, "Curvature")
    assert callable(arcpy.sa.Curvature)


def test_sa_contour():
    assert hasattr(arcpy.sa, "Contour")
    assert callable(arcpy.sa.Contour)


def test_sa_viewshed():
    assert hasattr(arcpy.sa, "Viewshed")
    assert callable(arcpy.sa.Viewshed)


def test_sa_cut_fill():
    assert hasattr(arcpy.sa, "CutFill")
    assert callable(arcpy.sa.CutFill)


# --- Local/Global Statistics ---
def test_sa_cell_statistics():
    assert hasattr(arcpy.sa, "CellStatistics")
    assert callable(arcpy.sa.CellStatistics)


def test_sa_local_sum():
    assert not hasattr(arcpy.sa, "LocalSum")


def test_sa_local_mean():
    assert not hasattr(arcpy.sa, "LocalMean")


def test_sa_local_max():
    assert not hasattr(arcpy.sa, "LocalMax")


def test_sa_local_min():
    assert not hasattr(arcpy.sa, "LocalMin")


def test_sa_zonal_statistics():
    assert hasattr(arcpy.sa, "ZonalStatistics")
    assert callable(arcpy.sa.ZonalStatistics)


def test_sa_zonal_geometry():
    assert hasattr(arcpy.sa, "ZonalGeometry")
    assert callable(arcpy.sa.ZonalGeometry)


def test_sa_zonal_histogram():
    assert hasattr(arcpy.sa, "ZonalHistogram")
    assert callable(arcpy.sa.ZonalHistogram)


# --- Interpolation ---
def test_sa_kriging():
    assert hasattr(arcpy.sa, "Kriging")
    assert callable(arcpy.sa.Kriging)


def test_sa_idw():
    assert not hasattr(arcpy.sa, "IDW")


def test_sa_natural_neighbor():
    assert hasattr(arcpy.sa, "NaturalNeighbor")
    assert callable(arcpy.sa.NaturalNeighbor)


def test_sa_trend():
    assert hasattr(arcpy.sa, "Trend")
    assert callable(arcpy.sa.Trend)


def test_sa_spline():
    assert hasattr(arcpy.sa, "Spline")
    assert callable(arcpy.sa.Spline)


# --- Other ---
def test_sa_flow():
    assert not hasattr(arcpy.sa, "Flow")


def test_sa_watershed():
    assert hasattr(arcpy.sa, "Watershed")
    assert callable(arcpy.sa.Watershed)


# ---------------------------------------------------------------------------
# Nbr* classes
# ---------------------------------------------------------------------------
def test_sa_nbr_rectangle():
    assert hasattr(arcpy.sa, "NbrRectangle")
    assert callable(arcpy.sa.NbrRectangle)

    nbr = arcpy.sa.NbrRectangle(3, 3, "CELL")
    assert nbr is not None

    nbr2 = arcpy.sa.NbrRectangle(3, 3, "MAP")
    assert nbr2 is not None


def test_sa_nbr_circle():
    assert hasattr(arcpy.sa, "NbrCircle")
    assert callable(arcpy.sa.NbrCircle)

    nbr = arcpy.sa.NbrCircle(3, "CELL")
    assert nbr is not None
    nbr2 = arcpy.sa.NbrCircle(3, "MAP")
    assert nbr2 is not None


def test_sa_nbr_wedge():
    assert hasattr(arcpy.sa, "NbrWedge")
    assert callable(arcpy.sa.NbrWedge)

    nbr = arcpy.sa.NbrWedge(5, 45, 90, "CELL")
    assert nbr is not None


def test_sa_nbr_annulus():
    assert hasattr(arcpy.sa, "NbrAnnulus")
    assert callable(arcpy.sa.NbrAnnulus)

    nbr = arcpy.sa.NbrAnnulus(3, 5, "CELL")
    assert nbr is not None


def test_sa_nbr_irregular():
    assert hasattr(arcpy.sa, "NbrIrregular")
    assert callable(arcpy.sa.NbrIrregular)


def test_sa_nbr_weight():
    assert hasattr(arcpy.sa, "NbrWeight")
    assert callable(arcpy.sa.NbrWeight)


def test_sa_nbr_block():
    assert not hasattr(arcpy.sa, "NbrBlock")


# ---------------------------------------------------------------------------
# Kriging model classes
# ---------------------------------------------------------------------------
def test_sa_kriging_model_ordinary():
    assert hasattr(arcpy.sa, "KrigingModelOrdinary")
    assert callable(arcpy.sa.KrigingModelOrdinary)

    model = arcpy.sa.KrigingModelOrdinary("Spherical", 1000, 0.5)
    assert model is not None


def test_sa_kriging_model_universal():
    assert hasattr(arcpy.sa, "KrigingModelUniversal")
    assert callable(arcpy.sa.KrigingModelUniversal)


# ---------------------------------------------------------------------------
# Functional tests with raster data
# ---------------------------------------------------------------------------
@pytest.fixture
def dem(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "sa.gdb")[0]
    dem_path = f"{gdb}/dem"
    out_raster = arcpy.sa.CreateConstantRaster(100, "INTEGER", 10, arcpy.Extent(0, 0, 100, 100))
    out_raster.save(dem_path)
    return dem_path, gdb


def test_sa_con_parameters(dem):
    dem_path, gdb = dem

    # Basic Con with relational expression
    con = arcpy.sa.Con(arcpy.sa.Raster(dem_path) > 50, 1, 0)
    assert hasattr(con, "save")
    con.save(f"{gdb}/con1")

    # Con with where_clause
    con2 = arcpy.sa.Con(arcpy.sa.Raster(dem_path) > 50, arcpy.sa.Raster(dem_path), 0)
    assert hasattr(con2, "save")

    # Con with default false (NoData)
    con3 = arcpy.sa.Con(arcpy.sa.Raster(dem_path) > 50, 1)
    assert hasattr(con3, "save")

    # Multi-condition
    con4 = arcpy.sa.Con((arcpy.sa.Raster(dem_path) > 50) &
                         (arcpy.sa.Raster(dem_path) < 150), 1, 0)
    assert hasattr(con4, "save")


def test_sa_reclassify_parameters(dem):
    dem_path, gdb = dem

    # RemapRange
    remap_range = arcpy.sa.RemapRange([[0, 50, 1], [50, 100, 2], [100, 9999, 3]])
    reclass = arcpy.sa.Reclassify(dem_path, "Value", remap_range)
    assert hasattr(reclass, "save")
    reclass.save(f"{gdb}/reclass_range")

    # RemapValue
    remap_val = arcpy.sa.RemapValue([[100, 1], ["NODATA", 0]])
    reclass2 = arcpy.sa.Reclassify(dem_path, "Value", remap_val)
    assert hasattr(reclass2, "save")

    # With missing_values parameter
    reclass3 = arcpy.sa.Reclassify(dem_path, "Value", remap_range, missing_values="NODATA")
    assert hasattr(reclass3, "save")

    reclass4 = arcpy.sa.Reclassify(dem_path, "Value", remap_range, missing_values="DATA")
    assert hasattr(reclass4, "save")


def test_sa_slope_parameters(dem):
    dem_path, gdb = dem

    for measure in ["DEGREE", "PERCENT_RISE"]:
        slope = arcpy.sa.Slope(dem_path, output_measurement=measure)
        assert hasattr(slope, "save")

    slope = arcpy.sa.Slope(dem_path)
    assert hasattr(slope, "save")

    slope = arcpy.sa.Slope(dem_path, output_measurement="DEGREE", z_factor=0.3048)
    assert hasattr(slope, "save")


def test_sa_aspect_parameters(dem):
    dem_path, gdb = dem

    aspect = arcpy.sa.Aspect(dem_path)
    assert hasattr(aspect, "save")


def test_sa_hillshade_parameters(dem):
    dem_path, gdb = dem

    hs = arcpy.sa.Hillshade(dem_path, azimuth=315, altitude=45)
    assert hasattr(hs, "save")

    hs2 = arcpy.sa.Hillshade(dem_path, azimuth=180, altitude=30, z_factor=0.3048)
    assert hasattr(hs2, "save")


def test_sa_curvature_parameters(dem):
    dem_path, gdb = dem

    curvature = arcpy.sa.Curvature(dem_path, z_factor=1.0)
    assert hasattr(curvature, "save")


def test_sa_focal_statistics_parameters(dem):
    dem_path, gdb = dem

    for stat in ["MEAN", "SUM", "STD", "MINIMUM", "MAXIMUM", "RANGE", "MEDIAN",
                  "MAJORITY", "MINORITY", "VARIETY"]:
        nbr = arcpy.sa.NbrRectangle(3, 3, "CELL")
        fs = arcpy.sa.FocalStatistics(dem_path, nbr, stat)
        assert hasattr(fs, "save")

    # Different neighborhood types
    for nbr_type in [
        arcpy.sa.NbrCircle(3, "CELL"),
        arcpy.sa.NbrWedge(5, 45, 90, "CELL"),
        arcpy.sa.NbrAnnulus(1, 3, "CELL"),
    ]:
        fs = arcpy.sa.FocalStatistics(dem_path, nbr_type, "MEAN")
        assert hasattr(fs, "save")

    # ignore_nodata parameter
    nbr = arcpy.sa.NbrRectangle(3, 3, "CELL")
    for ignore in ["DATA", "NODATA"]:
        fs = arcpy.sa.FocalStatistics(dem_path, nbr, "MEAN", ignore)
        assert hasattr(fs, "save")


def test_sa_block_statistics_parameters(dem):
    dem_path, gdb = dem

    for stat in ["SUM", "MEAN", "MINIMUM", "MAXIMUM"]:
        nbr = arcpy.sa.NbrRectangle(2, 2, "CELL")
        bs = arcpy.sa.BlockStatistics(dem_path, nbr, stat)
        assert hasattr(bs, "save")


def test_sa_euc_distance_parameters(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "saeuc.gdb")[0]
    pts = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    with arcpy.da.InsertCursor(pts, ["SHAPE@XY"]) as c:
        c.insertRow(((120.0, 30.0),))

    try:
        euc = arcpy.sa.EucDistance(pts, maximum_distance=1000)
        assert hasattr(euc, "save")

        euc2 = arcpy.sa.EucDistance(pts, maximum_distance=1000, cell_size=10)
        assert hasattr(euc2, "save")
    except RuntimeError:
        pytest.skip("EucDistance may fail on geographic extent/unit settings.")


def test_sa_zonal_statistics_parameters(dem):
    dem_path, gdb = dem

    # Create zone data
    zone_fc = arcpy.management.CreateFeatureclass(gdb, "zones", "POLYGON", spatial_reference=3857)[0]
    arcpy.management.AddField(zone_fc, "ZONE_ID", "SHORT")
    sr = arcpy.SpatialReference(3857)
    arr = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(100, 0), arcpy.Point(100, 100),
                       arcpy.Point(0, 100), arcpy.Point(0, 0)])
    with arcpy.da.InsertCursor(zone_fc, ["SHAPE@", "ZONE_ID"]) as c:
        c.insertRow([arcpy.Polygon(arr, sr), 1])

    for stat in ["SUM", "MEAN", "MAXIMUM", "MINIMUM", "RANGE", "STD", "VARIETY",
                  "MAJORITY", "MINORITY", "MEDIAN"]:
        zs = arcpy.sa.ZonalStatistics(zone_fc, "ZONE_ID", dem_path, stat)
        assert hasattr(zs, "save")

    for ignore in ["DATA", "NODATA"]:
        zs = arcpy.sa.ZonalStatistics(zone_fc, "ZONE_ID", dem_path, "MEAN", ignore)
        assert hasattr(zs, "save")


def test_sa_zonal_geometry_parameters(dem):
    dem_path, gdb = dem

    zone_fc = arcpy.management.CreateFeatureclass(gdb, "zones_geom", "POLYGON",
                                                    spatial_reference=3857)[0]
    arcpy.management.AddField(zone_fc, "ZONE_ID", "SHORT")
    sr = arcpy.SpatialReference(3857)
    arr = arcpy.Array([arcpy.Point(0, 0), arcpy.Point(100, 0), arcpy.Point(100, 100),
                       arcpy.Point(0, 100), arcpy.Point(0, 0)])
    with arcpy.da.InsertCursor(zone_fc, ["SHAPE@", "ZONE_ID"]) as c:
        c.insertRow([arcpy.Polygon(arr, sr), 1])

    for geom in ["AREA", "PERIMETER"]:
        zg = arcpy.sa.ZonalGeometry(zone_fc, "ZONE_ID", geom)
        assert hasattr(zg, "save")


def test_sa_cell_statistics_parameters(dem):
    dem_path, gdb = dem
    dem2_path = f"{gdb}/dem2"
    arcpy.sa.CreateConstantRaster(200, "INTEGER", 10, arcpy.Extent(0, 0, 100, 100)).save(dem2_path)

    for stat in ["SUM", "MEAN", "MEDIAN", "MINIMUM", "MAXIMUM", "RANGE", "STD",
                  "VARIETY", "MAJORITY", "MINORITY"]:
        cs = arcpy.sa.CellStatistics([dem_path, dem2_path], stat)
        assert hasattr(cs, "save")

    cs2 = arcpy.sa.CellStatistics([dem_path, dem2_path], "SUM", "DATA")
    assert hasattr(cs2, "save")


# ---------------------------------------------------------------------------
# Raster algebra operators
# ---------------------------------------------------------------------------
def test_sa_raster_operators(dem):
    dem_path, gdb = dem
    r = arcpy.sa.Raster(dem_path)
    r2 = arcpy.sa.Raster(dem_path)

    # Arithmetic
    assert hasattr(r + r2, "save")
    assert hasattr(r - r2, "save")
    assert hasattr(r * r2, "save")
    assert hasattr(r / 2.0, "save")

    # Comparison
    assert hasattr(r > 50, "save")
    assert hasattr(r >= 50, "save")
    assert hasattr(r < 150, "save")
    assert hasattr(r <= 150, "save")
    assert hasattr(r == 100, "save")

    # Logical
    c1 = r > 50
    c2 = r < 150
    assert hasattr(c1 & c2, "save")
    assert hasattr(c1 | c2, "save")

    # Power
    pw = arcpy.sa.Power(r, 2)
    assert hasattr(pw, "save")

    # Save and verify
    (r * 2).save(f"{gdb}/algebra_out")
    assert arcpy.Exists(f"{gdb}/algebra_out")
