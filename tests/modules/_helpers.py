from __future__ import annotations

import contextlib
import os
import shutil
import tempfile
import time
from glob import glob
from pathlib import Path

import arcpy


@contextlib.contextmanager
def arcgis_temp_workspace():
    tmp_dir = Path(tempfile.mkdtemp(prefix="arcpy_hf_"))
    try:
        yield tmp_dir
    finally:
        with contextlib.suppress(Exception):
            arcpy.ClearWorkspaceCache_management()
        for _ in range(6):
            try:
                shutil.rmtree(tmp_dir)
                break
            except PermissionError:
                time.sleep(0.5)


def new_file_gdb(tmp_dir: Path, name: str = "work.gdb") -> str:
    return arcpy.management.CreateFileGDB(str(tmp_dir), name)[0]


def create_point_fc(gdb: str, name: str = "pts", with_value: bool = True) -> str:
    fc = arcpy.management.CreateFeatureclass(gdb, name, "POINT", spatial_reference=4326)[0]
    arcpy.management.AddField(fc, "VALUE", "DOUBLE")
    if with_value:
        with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "VALUE"]) as cursor:
            cursor.insertRow(((120.0, 30.0), 10.0))
            cursor.insertRow(((120.01, 30.01), 20.0))
            cursor.insertRow(((120.02, 30.0), 30.0))
    return fc


def create_polygon_fc(gdb: str, name: str = "poly") -> str:
    fc = arcpy.management.CreateFeatureclass(gdb, name, "POLYGON", spatial_reference=4326)[0]
    arr = arcpy.Array(
        [
            arcpy.Point(119.99, 29.99),
            arcpy.Point(120.03, 29.99),
            arcpy.Point(120.03, 30.03),
            arcpy.Point(119.99, 30.03),
            arcpy.Point(119.99, 29.99),
        ]
    )
    with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as cursor:
        cursor.insertRow([arcpy.Polygon(arr, arcpy.SpatialReference(4326))])
    return fc


def try_create_temp_aprx(tmp_dir: Path) -> str | None:
    program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
    patterns = [
        rf"{program_files}\ArcGIS\Pro\Resources\ProjectTemplates\**\*.aprx",
        rf"{program_files}\ArcGIS\Pro\Resources\Templates\**\*.aprx",
        rf"{program_files}\ArcGIS\Pro\Resources\ProjectTemplates\**\*.aptx",
        rf"{program_files}\ArcGIS\Pro\Resources\Templates\**\*.aptx",
    ]
    for pattern in patterns:
        matches = glob(pattern, recursive=True)
        if matches:
            src = Path(matches[0])
            dst = tmp_dir / "auto-created.aprx"
            if src.suffix.lower() == ".aprx":
                shutil.copy2(src, dst)
                return str(dst)
            # For .aptx template, try creating a project via geoprocessing tool.
            if hasattr(arcpy.management, "CreateProject"):
                try:
                    result = arcpy.management.CreateProject(str(tmp_dir), dst.name, str(src))
                    created = Path(result[0])
                    if created.exists():
                        return str(created)
                except Exception:
                    continue
    return None
