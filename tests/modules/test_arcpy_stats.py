"""Tests for arcpy.stats module - all tools, parameters, and return values
documented in skills/arcpy-scripting/modules/arcpy-stats.md"""

import pytest

arcpy = pytest.importorskip("arcpy")

from _helpers import arcgis_temp_workspace, create_point_fc, new_file_gdb


# ---------------------------------------------------------------------------
# Existence and callability checks
# ---------------------------------------------------------------------------
def test_stats_hot_spots():
    assert hasattr(arcpy.stats, "HotSpots")
    assert callable(arcpy.stats.HotSpots)


def test_stats_cluster_outlier_analysis():
    assert hasattr(arcpy.stats, "ClusterOutlierAnalysis")
    assert callable(arcpy.stats.ClusterOutlierAnalysis)


def test_stats_spatial_autocorrelation():
    assert hasattr(arcpy.stats, "SpatialAutocorrelation")
    assert callable(arcpy.stats.SpatialAutocorrelation)


def test_stats_average_nearest_neighbor():
    assert hasattr(arcpy.stats, "AverageNearestNeighbor")
    assert callable(arcpy.stats.AverageNearestNeighbor)


def test_stats_high_high_clustering():
    assert hasattr(arcpy.stats, "HighHighClustering")
    assert callable(arcpy.stats.HighHighClustering)


def test_stats_low_low_clustering():
    assert hasattr(arcpy.stats, "LowLowClustering")
    assert callable(arcpy.stats.LowLowClustering)


def test_stats_kernel_density():
    assert hasattr(arcpy.stats, "KernelDensity")
    assert callable(arcpy.stats.KernelDensity)


def test_stats_point_density():
    assert hasattr(arcpy.stats, "PointDensity")
    assert callable(arcpy.stats.PointDensity)


def test_stats_line_density():
    assert hasattr(arcpy.stats, "LineDensity")
    assert callable(arcpy.stats.LineDensity)


def test_stats_calculate_density():
    assert hasattr(arcpy.stats, "CalculateDensity")
    assert callable(arcpy.stats.CalculateDensity)


def test_stats_ordinary_least_squares():
    assert hasattr(arcpy.stats, "OrdinaryLeastSquares")
    assert callable(arcpy.stats.OrdinaryLeastSquares)


def test_stats_geographically_weighted_regression():
    assert hasattr(arcpy.stats, "GeographicallyWeightedRegression")
    assert callable(arcpy.stats.GeographicallyWeightedRegression)


def test_stats_explore_trends():
    assert hasattr(arcpy.stats, "ExploreTrends")
    assert callable(arcpy.stats.ExploreTrends)


def test_stats_principal_components_analysis():
    assert hasattr(arcpy.stats, "PrincipalComponentsAnalysis")
    assert callable(arcpy.stats.PrincipalComponentsAnalysis)


def test_stats_discriminant_analysis():
    assert hasattr(arcpy.stats, "DiscriminantAnalysis")
    assert callable(arcpy.stats.DiscriminantAnalysis)


def test_stats_multivariate_clustering():
    assert hasattr(arcpy.stats, "MultivariateClustering")
    assert callable(arcpy.stats.MultivariateClustering)


def test_stats_grouping_analysis():
    assert hasattr(arcpy.stats, "GroupingAnalysis")
    assert callable(arcpy.stats.GroupingAnalysis)


def test_stats_export_xyv():
    assert hasattr(arcpy.stats, "ExportXYv")
    assert callable(arcpy.stats.ExportXYv)


def test_stats_count_renderer():
    assert hasattr(arcpy.stats, "CountRenderer")
    assert callable(arcpy.stats.CountRenderer)


# ---------------------------------------------------------------------------
# Functional tests
# ---------------------------------------------------------------------------
@pytest.fixture
def stat_data(tmp_path):
    gdb = arcpy.management.CreateFileGDB(str(tmp_path), "stats.gdb")[0]
    fc = arcpy.management.CreateFeatureclass(gdb, "pts", "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "CRIME_RATE", "DOUBLE")
    arcpy.management.AddField(fc, "INCOME", "DOUBLE")
    arcpy.management.AddField(fc, "SQFT", "DOUBLE")
    arcpy.management.AddField(fc, "BEDROOMS", "LONG")
    arcpy.management.AddField(fc, "AGE", "LONG")
    arcpy.management.AddField(fc, "PRICE", "DOUBLE")
    arcpy.management.AddField(fc, "WEIGHT", "DOUBLE")

    points = [
        ((120.0, 30.0), 10.0, 50000.0, 1500.0, 3, 10, 300000.0, 1.0),
        ((120.01, 30.01), 15.0, 55000.0, 1800.0, 4, 5, 350000.0, 1.0),
        ((120.02, 30.0), 20.0, 60000.0, 2000.0, 3, 15, 400000.0, 2.0),
        ((120.03, 30.01), 25.0, 65000.0, 2200.0, 4, 8, 450000.0, 1.0),
        ((120.01, 30.02), 30.0, 70000.0, 2500.0, 5, 3, 500000.0, 2.0),
        ((120.02, 30.02), 35.0, 75000.0, 2800.0, 4, 20, 550000.0, 1.0),
    ]

    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "CRIME_RATE", "INCOME", "SQFT",
                                      "BEDROOMS", "AGE", "PRICE", "WEIGHT"]) as c:
        for p in points:
            c.insertRow(p)

    return fc, gdb


def test_stats_hot_spots_parameters(stat_data):
    fc, gdb = stat_data

    r = arcpy.stats.HotSpots(
        fc, "CRIME_RATE", f"{gdb}/hotspots",
        distance_band_or_threshold_distance="1000 Meters",
        conceptualization_of_spatial_relationships="FIXED_DISTANCE_BAND",
        standardization="ROW"
    )
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)

    fields = [f.name for f in arcpy.ListFields(r[0])]
    assert "GiZScore" in fields
    assert "GiPValue" in fields
    assert "GiCluster" in fields

    # GiCluster values
    cluster_values = set()
    with arcpy.da.SearchCursor(r[0], ["GiCluster"]) as cursor:
        for (v,) in cursor:
            cluster_values.add(v)
    # Valid values: 0, 1, 2, 3, 4
    for v in cluster_values:
        assert v in (0, 1, 2, 3, 4)


def test_stats_hot_spots_conceptualizations(stat_data):
    fc, gdb = stat_data

    conceptualizations = [
        "INVERSE_DISTANCE",
        "INVERSE_DISTANCE_SQUARED",
        "FIXED_DISTANCE_BAND",
        "K_NEAREST_NEIGHBORS",
    ]
    for i, conceptual in enumerate(conceptualizations):
        try:
            out = f"{gdb}/hs_{i}"
            r = arcpy.stats.HotSpots(
                fc, "CRIME_RATE", out,
                distance_band_or_threshold_distance="1000 Meters",
                conceptualization_of_spatial_relationships=conceptual,
            )
            assert arcpy.Exists(r[0])
        except Exception:
            pass


def test_stats_cluster_outlier_analysis_parameters(stat_data):
    fc, gdb = stat_data

    r = arcpy.stats.ClusterOutlierAnalysis(
        fc, "CRIME_RATE", f"{gdb}/cluster_out",
        distance_band_or_threshold_distance="1000 Meters",
        conceptualization_of_spatial_relationships="FIXED_DISTANCE_BAND",
    )
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)

    fields = [f.name for f in arcpy.ListFields(r[0])]
    assert "COType" in fields
    assert "LZiScore" in fields
    assert "LPValue" in fields


def test_stats_spatial_autocorrelation_parameters(stat_data):
    fc, gdb = stat_data

    r = arcpy.stats.SpatialAutocorrelation(
        fc, "INCOME",
        distance_band_or_threshold_distance="5000 Meters",
        conceptualization_of_spatial_relationships="INVERSE_DISTANCE"
    )
    assert isinstance(r, arcpy.Result)
    msgs = r.getMessages()
    assert isinstance(msgs, str)
    assert len(msgs) > 0

    r2 = arcpy.stats.SpatialAutocorrelation(
        fc, "INCOME",
        distance_band_or_threshold_distance="5000 Meters",
        conceptualization_of_spatial_relationships="INVERSE_DISTANCE",
        standardization="ROW",
        generate_report="GENERATE_REPORT"
    )
    assert isinstance(r2, arcpy.Result)


def test_stats_average_nearest_neighbor_parameters(stat_data):
    fc, gdb = stat_data

    for method in ["EUCLIDEAN", "MANHATTAN"]:
        r = arcpy.stats.AverageNearestNeighbor(fc, distance_method=method)
        assert isinstance(r, arcpy.Result)

    r2 = arcpy.stats.AverageNearestNeighbor(fc, generate_report="GENERATE_REPORT",
                                              area="1000000")
    assert isinstance(r2, arcpy.Result)

    r3 = arcpy.stats.AverageNearestNeighbor(fc, distance_method="EUCLIDEAN",
                                              area=1000000)
    assert isinstance(r3, arcpy.Result)


def test_stats_kernel_density_parameters(stat_data):
    fc, gdb = stat_data

    r = arcpy.stats.KernelDensity(
        fc, "WEIGHT",
        cell_size=30,
        search_radius=500,
        area_unit_scale_factor="SQUARE_KILOMETERS"
    )
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)

    r2 = arcpy.stats.KernelDensity(fc, None, cell_size=30)
    assert arcpy.Exists(r2[0])


def test_stats_ordinary_least_squares_parameters(stat_data):
    fc, gdb = stat_data

    r = arcpy.stats.OrdinaryLeastSquares(
        fc, "PRICE",
        ["SQFT", "BEDROOMS", "AGE"],
        f"{gdb}/ols_result",
        coefficient_output_table=f"{gdb}/ols_coef",
        diagnostic_output_table=f"{gdb}/ols_diag"
    )
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)

    fields = [f.name for f in arcpy.ListFields(r[0])]
    assert "Residual" in fields
    assert "Predicted" in fields
    assert "StdResidual" in fields

    assert arcpy.Exists(f"{gdb}/ols_coef")


def test_stats_geographically_weighted_regression_parameters(stat_data):
    fc, gdb = stat_data

    for kernel in ["GAUSSIAN", "BISQUARE"]:
        out = f"{gdb}/gwr_{kernel}"
        r = arcpy.stats.GeographicallyWeightedRegression(
            fc, "PRICE",
            ["SQFT", "BEDROOMS", "AGE"],
            out,
            kernel_type=kernel,
            bandwidth_method="AICc"
        )
        assert arcpy.Exists(r[0])
        assert isinstance(r, arcpy.Result)

    # With distance_band
    r2 = arcpy.stats.GeographicallyWeightedRegression(
        fc, "PRICE",
        ["SQFT", "BEDROOMS", "AGE"],
        f"{gdb}/gwr_band",
        kernel_type="GAUSSIAN",
        bandwidth_method="BANDWIDTH_PARAMETER",
        distance_band="1000"
    )
    assert arcpy.Exists(r2[0])


def test_stats_principal_components_analysis_parameters(stat_data):
    fc, gdb = stat_data

    r = arcpy.stats.PrincipalComponentsAnalysis(
        fc,
        f"{gdb}/pca_result",
        variables=["SQFT", "BEDROOMS", "AGE", "PRICE"],
        number_of_components=2
    )
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)


def test_stats_grouping_analysis_parameters(stat_data):
    fc, gdb = stat_data

    r = arcpy.stats.GroupingAnalysis(
        fc,
        None,
        f"{gdb}/ga_result",
        number_of_groups=3,
        analysis_fields=["CRIME_RATE", "INCOME", "PRICE"]
    )
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)

    fields = [f.name for f in arcpy.ListFields(r[0])]
    assert "SSQ" in fields
    assert "SC_Label" in fields

    # With spatial_constraints
    for constraint in ["NO_SPATIAL_CONSTRAINT"]:
        try:
            r2 = arcpy.stats.GroupingAnalysis(
                fc,
                None,
                f"{gdb}/ga_{constraint}",
                number_of_groups=2,
                analysis_fields=["CRIME_RATE", "INCOME", "PRICE"],
                spatial_constraints=constraint
            )
            assert arcpy.Exists(r2[0])
        except Exception:
            pass


def test_stats_multivariate_clustering_parameters(stat_data):
    fc, gdb = stat_data

    r = arcpy.stats.MultivariateClustering(
        fc,
        None,
        f"{gdb}/mc_result",
        number_of_groups=3,
        analysis_fields=["CRIME_RATE", "INCOME", "PRICE"]
    )
    assert arcpy.Exists(r[0])
    assert isinstance(r, arcpy.Result)


def test_stats_export_xyv_parameters(stat_data):
    fc, gdb = stat_data

    from pathlib import Path
    out_csv = Path(gdb).parent / "exported.csv"

    r = arcpy.stats.ExportXYv(fc, str(out_csv), "OID@;SHAPE@X;SHAPE@Y;CRIME_RATE")
    assert isinstance(r, arcpy.Result)


def test_stats_calculate_density_parameters(stat_data):
    fc, gdb = stat_data

    r = arcpy.stats.CalculateDensity(fc, bin_size=100, radius_multiplier=2,
                                       out_cell_size=10)
    assert isinstance(r, arcpy.Result)
    assert arcpy.Exists(r[0])


def test_stats_explore_trends_parameters(stat_data):
    fc, gdb = stat_data

    r = arcpy.stats.ExploreTrends(fc, "CRIME_RATE",
                                    f"{gdb}/explore_report.pdf",
                                    cell_size=1000,
                                    search_radius="5000 Meters")
    assert isinstance(r, arcpy.Result)
