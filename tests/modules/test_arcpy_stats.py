import pytest

arcpy = pytest.importorskip("arcpy")


def test_arcpy_stats_parameters_are_really_usable() -> None:
    assert hasattr(arcpy.stats, "AverageNearestNeighbor")
    assert callable(arcpy.stats.AverageNearestNeighbor)
