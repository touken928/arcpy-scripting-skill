import pytest

arcpy = pytest.importorskip("arcpy")


def test_arcpy_sa_parameters_are_really_usable() -> None:
    assert hasattr(arcpy.sa, "Con")
    assert hasattr(arcpy.sa, "Reclassify")
    assert callable(arcpy.sa.Con)
    assert callable(arcpy.sa.Reclassify)
