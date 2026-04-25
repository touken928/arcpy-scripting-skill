import pytest

arcpy = pytest.importorskip("arcpy")


def test_arcpy_mp_parameters_are_really_usable() -> None:
    # arcpy.mp is used to operate existing projects; it does not guarantee project creation.
    assert hasattr(arcpy.mp, "ArcGISProject")
    assert callable(arcpy.mp.ArcGISProject)
