from __future__ import annotations

import argparse
from pathlib import Path

import arcpy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a GeoPackage and a sample point feature class."
    )
    parser.add_argument(
        "--out-folder",
        default=str(Path.cwd() / "examples_output"),
        help="Output parent folder path (default: ./examples_output).",
    )
    parser.add_argument("--gpkg-name", default="demo.gpkg", help="GeoPackage name.")
    parser.add_argument("--fc-name", default="sample_points", help="Output feature class name.")
    parser.add_argument(
        "--spatial-ref",
        type=int,
        default=4326,
        help="EPSG WKID for output feature class spatial reference.",
    )
    return parser.parse_args()


def ensure_geopackage(out_folder: Path, gpkg_name: str = "demo.gpkg") -> str:
    out_folder.mkdir(parents=True, exist_ok=True)
    gpkg_path = out_folder / gpkg_name
    if arcpy.Exists(str(gpkg_path)):
        return str(gpkg_path)
    return arcpy.management.CreateSQLiteDatabase(str(gpkg_path), "GEOPACKAGE")[0]


def create_demo_points(workspace: str, fc_name: str = "sample_points", wkid: int = 4326) -> str:
    out_fc = f"{workspace}/{fc_name}"
    if arcpy.Exists(out_fc):
        arcpy.management.Delete(out_fc)
    sr = arcpy.SpatialReference(wkid)
    arcpy.management.CreateFeatureclass(workspace, fc_name, "POINT", spatial_reference=sr)
    arcpy.management.AddField(out_fc, "NAME", "TEXT", field_length=50)
    arcpy.management.AddField(out_fc, "VALUE", "LONG")
    rows = [
        ("P1", 10, (120.10, 30.20)),
        ("P2", 20, (120.12, 30.24)),
        ("P3", 30, (120.08, 30.18)),
        ("P4", 40, (120.15, 30.26)),
    ]
    with arcpy.da.InsertCursor(out_fc, ["NAME", "VALUE", "SHAPE@XY"]) as cur:
        for row in rows:
            cur.insertRow(row)
    return out_fc


def main() -> int:
    args = parse_args()
    arcpy.env.overwriteOutput = True

    try:
        out_folder = Path(args.out_folder).expanduser().resolve()
        gpkg = ensure_geopackage(out_folder, args.gpkg_name)
        out_fc = create_demo_points(gpkg, args.fc_name, args.spatial_ref)
        print(f"Created sample data: {out_fc}")
        return 0
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        return 1
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
