# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import arcpy


TOOLBOX_ALIAS = "sample_count"
DEMO_GPKG_NAME = "sample_toolbox_demo.gpkg"


class Toolbox(object):
    def __init__(self) -> None:
        self.label = "Sample Count Features Toolbox"
        self.alias = TOOLBOX_ALIAS
        self.tools = [CountFeaturesTool]


class CountFeaturesTool(object):
    def __init__(self) -> None:
        self.label = "Count Features"
        self.description = "Count rows in a feature class or feature layer."
        self.canRunInBackground = False

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        in_features = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
        )
        out_count = arcpy.Parameter(
            displayName="Feature Count",
            name="out_count",
            datatype="GPLong",
            parameterType="Derived",
            direction="Output",
        )
        return [in_features, out_count]

    def execute(self, parameters: list[arcpy.Parameter], messages: object) -> None:
        count = count_features(parameters[0].valueAsText)
        messages.addMessage(f"Feature count: {count}")
        parameters[1].value = count


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the sample Python toolbox logic from the command line. If "
            "--in-features is omitted, a small demo GeoPackage feature class is created."
        )
    )
    parser.add_argument(
        "--out-folder",
        default=str(Path.cwd() / "examples_output"),
        help="Output parent folder for generated demo data (default: ./examples_output).",
    )
    parser.add_argument(
        "--gpkg-name",
        default=DEMO_GPKG_NAME,
        help="Demo GeoPackage name used when --in-features is omitted.",
    )
    parser.add_argument(
        "--in-features",
        help="Existing feature class or feature layer to count.",
    )
    return parser.parse_args(argv)


def ensure_geopackage(out_folder: Path, gpkg_name: str) -> str:
    out_folder.mkdir(parents=True, exist_ok=True)
    gpkg_path = out_folder / gpkg_name
    if arcpy.Exists(str(gpkg_path)):
        return str(gpkg_path)
    return str(arcpy.management.CreateSQLiteDatabase(str(gpkg_path), "GEOPACKAGE")[0])


def create_demo_points(workspace: str, fc_name: str = "sample_points", wkid: int = 4326) -> str:
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
    ]
    with arcpy.da.InsertCursor(out_fc, ["NAME", "SHAPE@XY"]) as cur:
        for row in rows:
            cur.insertRow(row)
    return out_fc


def count_features(in_features: str) -> int:
    if not arcpy.Exists(in_features):
        raise ValueError(f"Input features not found: {in_features}")
    return int(arcpy.management.GetCount(in_features)[0])


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    arcpy.env.overwriteOutput = True

    try:
        if args.in_features:
            in_features = args.in_features
        else:
            out_folder = Path(args.out_folder).expanduser().resolve()
            gpkg = ensure_geopackage(out_folder, args.gpkg_name)
            in_features = create_demo_points(gpkg)

        print(f"Input features: {in_features}")
        print(f"Feature count: {count_features(in_features)}")
        return 0
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        return 1
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        return 1


def is_direct_cli_run() -> bool:
    if not sys.argv or not sys.argv[0]:
        return False
    try:
        return Path(sys.argv[0]).resolve() == Path(__file__).resolve()
    except (OSError, RuntimeError):
        return False


if __name__ == "__main__" and is_direct_cli_run():
    raise SystemExit(main())
