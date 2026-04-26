from __future__ import annotations

import argparse
from pathlib import Path

import arcpy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create demo data, then run buffer and clip workflow."
    )
    parser.add_argument(
        "--out-folder",
        default=str(Path.cwd() / "examples_output"),
        help="Output parent folder path (default: ./examples_output).",
    )
    parser.add_argument("--gpkg-name", default="buffer_clip_demo.gpkg", help="Output GeoPackage name.")
    parser.add_argument(
        "--buffer-distance",
        default="200 Meters",
        help='Buffer distance string, for example "200 Meters".',
    )
    return parser.parse_args()


def ensure_geopackage(out_folder: Path, gpkg_name: str = "buffer_clip_demo.gpkg") -> str:
    out_folder.mkdir(parents=True, exist_ok=True)
    gpkg_path = out_folder / gpkg_name
    if arcpy.Exists(str(gpkg_path)):
        return str(gpkg_path)
    return arcpy.management.CreateSQLiteDatabase(str(gpkg_path), "GEOPACKAGE")[0]


def create_demo_points(workspace: str, fc_name: str = "input_points", wkid: int = 4326) -> str:
    out_fc = f"{workspace}/{fc_name}"
    if arcpy.Exists(out_fc):
        arcpy.management.Delete(out_fc)
    sr = arcpy.SpatialReference(wkid)
    arcpy.management.CreateFeatureclass(workspace, fc_name, "POINT", spatial_reference=sr)
    arcpy.management.AddField(out_fc, "NAME", "TEXT", field_length=50)
    rows = [
        ("P1", (120.10, 30.20)),
        ("P2", (120.12, 30.24)),
        ("P3", (120.08, 30.18)),
        ("P4", (120.15, 30.26)),
    ]
    with arcpy.da.InsertCursor(out_fc, ["NAME", "SHAPE@XY"]) as cur:
        for row in rows:
            cur.insertRow(row)
    return out_fc


def create_demo_clip_polygon(workspace: str, fc_name: str = "clip_boundary", wkid: int = 4326) -> str:
    out_fc = f"{workspace}/{fc_name}"
    if arcpy.Exists(out_fc):
        arcpy.management.Delete(out_fc)
    sr = arcpy.SpatialReference(wkid)
    arcpy.management.CreateFeatureclass(workspace, fc_name, "POLYGON", spatial_reference=sr)
    ring = arcpy.Array(
        [
            arcpy.Point(120.05, 30.15),
            arcpy.Point(120.20, 30.15),
            arcpy.Point(120.20, 30.30),
            arcpy.Point(120.05, 30.30),
            arcpy.Point(120.05, 30.15),
        ]
    )
    with arcpy.da.InsertCursor(out_fc, ["SHAPE@"]) as cur:
        cur.insertRow([arcpy.Polygon(ring, sr)])
    return out_fc


def main() -> int:
    args = parse_args()
    arcpy.env.overwriteOutput = True

    try:
        out_folder = Path(args.out_folder).expanduser().resolve()
        gpkg = ensure_geopackage(out_folder, args.gpkg_name)
        in_features = create_demo_points(gpkg, "input_points")
        clip_features = create_demo_clip_polygon(gpkg, "clip_boundary")
        out_buffer = f"{gpkg}/buffer_result"
        out_clip = f"{gpkg}/clip_result"

        arcpy.analysis.Buffer(
            in_features,
            out_buffer,
            args.buffer_distance,
            dissolve_option="ALL",
        )
        arcpy.analysis.Clip(out_buffer, clip_features, out_clip)

        print(f"Input features: {in_features}")
        print(f"Clip boundary: {clip_features}")
        print(f"Buffer output: {out_buffer}")
        print(f"Clip output: {out_clip}")
        return 0
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        return 1
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
