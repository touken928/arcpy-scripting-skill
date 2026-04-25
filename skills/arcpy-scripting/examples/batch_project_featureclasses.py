from __future__ import annotations

import argparse
from pathlib import Path

import arcpy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create demo feature classes, then project all of them to a target WKID."
    )
    parser.add_argument(
        "--out-folder",
        default=str(Path.cwd() / "examples_output"),
        help="Output parent folder path (default: ./examples_output).",
    )
    parser.add_argument("--in-gdb-name", default="project_src_demo.gdb", help="Input gdb name.")
    parser.add_argument("--out-gdb-name", default="project_out_demo.gdb", help="Output gdb name.")
    parser.add_argument(
        "--wkid",
        type=int,
        default=3857,
        help="Target spatial reference WKID (default: 3857).",
    )
    parser.add_argument(
        "--suffix",
        default="_prj",
        help="Suffix to append to projected output feature classes.",
    )
    return parser.parse_args()


def ensure_gdb(out_folder: Path, gdb_name: str) -> str:
    out_folder.mkdir(parents=True, exist_ok=True)
    gdb_path = out_folder / gdb_name
    if arcpy.Exists(str(gdb_path)):
        return str(gdb_path)
    return arcpy.management.CreateFileGDB(str(out_folder), gdb_name)[0]


def create_demo_featureclasses(gdb: str, wkid: int = 4326) -> None:
    sr = arcpy.SpatialReference(wkid)
    points_fc = f"{gdb}/cities"
    lines_fc = f"{gdb}/roads"

    for fc_path, geometry in [(points_fc, "POINT"), (lines_fc, "POLYLINE")]:
        if arcpy.Exists(fc_path):
            arcpy.management.Delete(fc_path)
        arcpy.management.CreateFeatureclass(gdb, Path(fc_path).name, geometry, spatial_reference=sr)

    with arcpy.da.InsertCursor(points_fc, ["SHAPE@XY"]) as cur:
        cur.insertRow(((120.10, 30.20),))
        cur.insertRow(((120.18, 30.22),))

    line = arcpy.Polyline(
        arcpy.Array([arcpy.Point(120.00, 30.10), arcpy.Point(120.25, 30.28)]),
        sr,
    )
    with arcpy.da.InsertCursor(lines_fc, ["SHAPE@"]) as cur:
        cur.insertRow([line])


def main() -> int:
    args = parse_args()
    arcpy.env.overwriteOutput = True

    try:
        out_folder = Path(args.out_folder).expanduser().resolve()
        in_gdb = ensure_gdb(out_folder, args.in_gdb_name)
        out_gdb = ensure_gdb(out_folder, args.out_gdb_name)
        create_demo_featureclasses(in_gdb)

        sr = arcpy.SpatialReference(args.wkid)

        arcpy.env.workspace = in_gdb
        fcs = arcpy.ListFeatureClasses()
        if not fcs:
            print("No feature classes found in input gdb.")
            return 0

        for fc in fcs:
            out_fc = f"{out_gdb}/{fc}{args.suffix}"
            arcpy.management.Project(fc, out_fc, sr)
            print(f"Projected: {fc} -> {out_fc}")
        return 0
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        return 1
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
