from __future__ import annotations

import argparse
from pathlib import Path

import arcpy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a demo point feature class in a File GDB, then export copies to "
            "Shapefile, another GDB feature class, GeoPackage, and GeoJSON."
        )
    )
    parser.add_argument(
        "--out-folder",
        default=str(Path.cwd() / "examples_output"),
        help="Output parent folder path (default: ./examples_output).",
    )
    parser.add_argument(
        "--gdb-name",
        default="vector_convert_src_demo.gdb",
        help="Source File GDB name containing the input feature class.",
    )
    parser.add_argument(
        "--out-gdb-name",
        default="vector_convert_out_demo.gdb",
        help="Target File GDB for FeatureClassToFeatureClass copy.",
    )
    parser.add_argument(
        "--skip-geojson",
        action="store_true",
        help="Skip FeaturesToJSON (GeoJSON) if your Pro build lacks the tool.",
    )
    return parser.parse_args()


def ensure_gdb(out_folder: Path, gdb_name: str) -> str:
    out_folder.mkdir(parents=True, exist_ok=True)
    gdb_path = out_folder / gdb_name
    if arcpy.Exists(str(gdb_path)):
        return str(gdb_path)
    return arcpy.management.CreateFileGDB(str(out_folder), gdb_name)[0]


def create_demo_points(gdb: str, fc_name: str = "source_points", wkid: int = 4326) -> str:
    out_fc = f"{gdb}/{fc_name}"
    if arcpy.Exists(out_fc):
        arcpy.management.Delete(out_fc)
    sr = arcpy.SpatialReference(wkid)
    arcpy.management.CreateFeatureclass(gdb, fc_name, "POINT", spatial_reference=sr)
    arcpy.management.AddField(out_fc, "NAME", "TEXT", field_length=50)
    arcpy.management.AddField(out_fc, "VALUE", "LONG")
    rows = [
        ("A", 1, (120.10, 30.20)),
        ("B", 2, (120.12, 30.24)),
        ("C", 3, (120.08, 30.18)),
    ]
    with arcpy.da.InsertCursor(out_fc, ["NAME", "VALUE", "SHAPE@XY"]) as cur:
        for row in rows:
            cur.insertRow(row)
    return out_fc


def export_shapefile(in_fc: str, out_folder: Path) -> str:
    shp_folder = out_folder / "shapefile_out"
    shp_folder.mkdir(parents=True, exist_ok=True)
    out_shp = shp_folder / "demo_points.shp"
    if arcpy.Exists(str(out_shp)):
        arcpy.management.Delete(str(out_shp))
    return str(arcpy.conversion.ExportFeatures(in_fc, str(out_shp))[0])


def copy_to_gdb(in_fc: str, out_gdb: str, out_name: str) -> str:
    out_path = f"{out_gdb}/{out_name}"
    if arcpy.Exists(out_path):
        arcpy.management.Delete(out_path)
    return str(arcpy.conversion.FeatureClassToFeatureClass(in_fc, out_gdb, out_name)[0])


def export_geopackage(in_fc: str, out_folder: Path) -> str:
    """Export requires an existing GeoPackage workspace; create it first."""
    gpkg_path = out_folder / "demo_vectors.gpkg"
    if arcpy.Exists(str(gpkg_path)):
        arcpy.management.Delete(str(gpkg_path))
    arcpy.management.CreateSQLiteDatabase(str(gpkg_path), "GEOPACKAGE")
    layer_path = f"{gpkg_path}/points_gpkg"
    return str(arcpy.conversion.ExportFeatures(in_fc, layer_path)[0])


def export_geojson(in_fc: str, out_folder: Path) -> str:
    out_file = out_folder / "demo_points.geojson"
    if out_file.exists():
        out_file.unlink()
    arcpy.conversion.FeaturesToJSON(
        in_fc,
        str(out_file),
        "NOT_FORMATTED",
        "NO_Z_VALUES",
        "NO_M_VALUES",
        "GEOJSON",
        "KEEP_INPUT_SR",
    )
    return str(out_file)


def shapefile_to_gdb(in_shp: str, out_gdb: str, out_name: str) -> str:
    """Demonstrate Shapefile -> File GDB using the same conversion API."""
    out_path = f"{out_gdb}/{out_name}"
    if arcpy.Exists(out_path):
        arcpy.management.Delete(out_path)
    return str(arcpy.conversion.FeatureClassToFeatureClass(in_shp, out_gdb, out_name)[0])


def main() -> int:
    args = parse_args()
    arcpy.env.overwriteOutput = True

    try:
        out_folder = Path(args.out_folder).expanduser().resolve()
        src_gdb = ensure_gdb(out_folder, args.gdb_name)
        out_gdb = ensure_gdb(out_folder, args.out_gdb_name)
        source_fc = create_demo_points(src_gdb, "source_points")
        expected = int(arcpy.management.GetCount(source_fc)[0])

        outputs: list[tuple[str, str]] = []
        shp_out = export_shapefile(source_fc, out_folder)
        outputs.append(("shapefile", shp_out))
        outputs.append(("file_gdb_fc", copy_to_gdb(source_fc, out_gdb, "points_from_gdb")))
        outputs.append(("geopackage", export_geopackage(source_fc, out_folder)))
        outputs.append(("shapefile_to_gdb", shapefile_to_gdb(shp_out, out_gdb, "points_from_shp")))

        if not args.skip_geojson:
            outputs.append(("geojson_file", export_geojson(source_fc, out_folder)))

        for label, path in outputs:
            if label == "geojson_file":
                if not Path(path).is_file():
                    print(f"{label}: missing file {path}")
                    return 1
                print(f"{label}: {path}")
                continue
            if not arcpy.Exists(path):
                print(f"{label}: missing dataset {path}")
                return 1
            count = int(arcpy.management.GetCount(path)[0])
            if count != expected:
                print(f"{label}: expected {expected} features, got {count} at {path}")
                return 1
            print(f"{label} ({count} features): {path}")

        print(f"Source: {source_fc}")
        return 0
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        return 1
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
