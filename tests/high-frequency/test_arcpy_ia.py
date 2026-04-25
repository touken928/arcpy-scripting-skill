import pytest

arcpy = pytest.importorskip("arcpy")


def test_arcpy_ia_parameters_are_really_usable() -> None:
    assert hasattr(arcpy.ia, "NDVI")
    assert hasattr(arcpy.ia, "SegmentMeanShift")
    assert callable(arcpy.ia.NDVI)
    assert callable(arcpy.ia.SegmentMeanShift)
