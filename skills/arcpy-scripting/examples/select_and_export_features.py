from __future__ import annotations

import argparse
from pathlib import Path

import arcpy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create demo points, then select by condition and export."
    )
    parser.add_argument(
        "--out-folder",
        default=str(Path.cwd() / "examples_output"),
        help="Output parent folder path (default: ./examples_output).",
    )
    parser.add_argument("--gpkg-name", default="select_export_demo.gpkg", help="Output GeoPackage name.")
    parser.add_argument("--where", default="VALUE >= 20", help="SQL where clause.")
    parser.add_argument("--layer-name", default="tmp_select_lyr", help="Temporary layer name.")
    return parser.parse_args()


def ensure_geopackage(out_folder: Path, gpkg_name: str = "select_export_demo.gpkg") -> str:
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
        in_features = create_demo_points(gpkg, "input_points")
        out_features = f"{gpkg}/selected_points"

        layer = arcpy.management.MakeFeatureLayer(in_features, args.layer_name)[0]
        arcpy.management.SelectLayerByAttribute(layer, "NEW_SELECTION", args.where)
        arcpy.conversion.ExportFeatures(layer, out_features)
        selected_count = int(arcpy.management.GetCount(out_features)[0])
        print(f"Selected and exported rows: {selected_count}")
        print(f"Input: {in_features}")
        print(f"Output: {out_features}")
        return 0
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        return 1
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
