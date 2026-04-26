# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

import arcpy


TOOLBOX_ALIAS = "csv2gpkg"
DIRECT_RUN_ENV = "CSV_TO_GEOPACKAGE_PYT_DIRECT_RUN"

RESERVED_FIELDS = {"geom_type", "wkt"}


def _normalize_geom_kind(raw: str) -> str:
    s = (raw or "").strip().upper()
    aliases = {
        "POINT": "POINT",
        "PT": "POINT",
        "POLYLINE": "POLYLINE",
        "LINE": "POLYLINE",
        "LINESTRING": "POLYLINE",
        "LINE_STRING": "POLYLINE",
        "MULTILINESTRING": "POLYLINE",
        "POLYGON": "POLYGON",
        "POLY": "POLYGON",
    }
    if s not in aliases:
        raise ValueError(f"Unsupported geom_type: {raw!r} (use POINT, POLYLINE/LINESTRING, POLYGON)")
    return aliases[s]


def _fc_name_for_kind(base: str, kind: str, multi: bool) -> str:
    if not multi:
        return base
    suffix = {"POINT": "_point", "POLYLINE": "_line", "POLYGON": "_polygon"}[kind]
    return f"{base}{suffix}"


def _collect_rows_by_kind(csv_path: Path) -> tuple[dict[str, list[dict[str, str]]], list[str]]:
    by_kind: dict[str, list[dict[str, str]]] = defaultdict(list)
    attr_fields: list[str] = []
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row.")
        headers = [h.strip() for h in reader.fieldnames if h and h.strip()]
        lower = {h.lower(): h for h in headers}
        if "geom_type" not in lower or "wkt" not in lower:
            raise ValueError("CSV must include geom_type and WKT columns (case-insensitive).")
        geom_key = lower["geom_type"]
        wkt_key = lower["wkt"]
        attr_fields = [h for h in headers if h.lower() not in RESERVED_FIELDS]

        for row in reader:
            if row is None:
                continue
            geom_raw = (row.get(geom_key) or "").strip()
            wkt = (row.get(wkt_key) or "").strip()
            if not geom_raw and not wkt:
                continue
            kind = _normalize_geom_kind(geom_raw)
            attrs = {h: (row.get(h) or "").strip() for h in attr_fields}
            by_kind[kind].append({"wkt": wkt, **attrs})

    if not by_kind:
        raise ValueError("No data rows found in CSV.")

    return by_kind, attr_fields


class Toolbox:
    def __init__(self) -> None:
        self.label = "CSV To GeoPackage"
        self.alias = TOOLBOX_ALIAS
        self.tools = [CsvToGeoPackageTool]


class CsvToGeoPackageTool:
    def __init__(self) -> None:
        self.label = "CSV To GeoPackage"
        self.description = (
            "Read a CSV with geom_type and WKT columns plus optional text fields, "
            "and write POINT / POLYLINE / POLYGON feature classes into a GeoPackage."
        )
        self.canRunInBackground = False

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        in_csv = arcpy.Parameter(
            displayName="Input CSV",
            name="in_csv",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        in_csv.filter.list = ["csv"]

        out_folder = arcpy.Parameter(
            displayName="Output Folder",
            name="out_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
        )

        gpkg_name = arcpy.Parameter(
            displayName="GeoPackage File Name",
            name="gpkg_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )

        feature_basename = arcpy.Parameter(
            displayName="Output Feature Basename",
            name="feature_basename",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        feature_basename.value = "imported"

        sr_wkid = arcpy.Parameter(
            displayName="Spatial Reference WKID",
            name="sr_wkid",
            datatype="GPLong",
            parameterType="Required",
            direction="Input",
        )
        sr_wkid.value = 4326

        return [in_csv, out_folder, gpkg_name, feature_basename, sr_wkid]

    def execute(self, parameters: list[arcpy.Parameter], messages: object) -> None:
        in_csv = Path(parameters[0].valueAsText).expanduser().resolve()
        out_folder = Path(parameters[1].valueAsText).expanduser().resolve()
        gpkg_name = parameters[2].valueAsText.strip()
        feature_basename = parameters[3].valueAsText.strip()
        sr_wkid = int(parameters[4].value)

        if not in_csv.is_file():
            raise ValueError(f"CSV not found: {in_csv}")
        if not gpkg_name.lower().endswith(".gpkg"):
            raise ValueError("gpkg_name must end with .gpkg")
        if not feature_basename:
            raise ValueError("feature_basename must not be empty.")

        out_folder.mkdir(parents=True, exist_ok=True)
        gpkg_path = out_folder / gpkg_name
        if arcpy.Exists(str(gpkg_path)):
            arcpy.management.Delete(str(gpkg_path))
        arcpy.management.CreateSQLiteDatabase(str(gpkg_path), "GEOPACKAGE")

        sr = arcpy.SpatialReference(sr_wkid)
        by_kind, attr_fields = _collect_rows_by_kind(in_csv)
        multi = len(by_kind) > 1

        shape_type = {"POINT": "POINT", "POLYLINE": "POLYLINE", "POLYGON": "POLYGON"}

        for kind, rows in by_kind.items():
            fc_short = arcpy.ValidateTableName(_fc_name_for_kind(feature_basename, kind, multi), str(gpkg_path))
            arcpy.management.CreateFeatureclass(
                str(gpkg_path),
                fc_short,
                shape_type[kind],
                spatial_reference=sr,
            )
            fc_path = f"{gpkg_path}/{fc_short}"
            field_specs: list[tuple[str, str]] = []
            used_safe: set[str] = set()
            for field in attr_fields:
                safe = arcpy.ValidateFieldName(field, fc_path)
                if safe.lower() in ("shape", "objectid", "fid"):
                    continue
                if safe.lower() in used_safe:
                    continue
                if any(f.name.lower() == safe.lower() for f in arcpy.ListFields(fc_path)):
                    continue
                arcpy.management.AddField(fc_path, safe, "TEXT", field_length=255)
                field_specs.append((field, safe))
                used_safe.add(safe.lower())

            field_names = ["SHAPE@"] + [safe for _, safe in field_specs]

            inserted = 0
            with arcpy.da.InsertCursor(fc_path, field_names) as cur:
                for row in rows:
                    wkt = row["wkt"].strip()
                    if not wkt:
                        continue
                    geom = arcpy.FromWKT(wkt, sr)
                    values: list[object] = [geom]
                    for orig, _safe in field_specs:
                        values.append(row.get(orig, ""))
                    cur.insertRow(values)
                    inserted += 1

            messages.addMessage(f"{fc_path}: inserted {inserted} features ({kind})")


if (
    Path(sys.argv[0]).resolve() == Path(__file__).resolve()
    and os.environ.get(DIRECT_RUN_ENV) != "1"
):
    parser = argparse.ArgumentParser(description="Import CSV WKT rows into a GeoPackage from the command line.")
    parser.add_argument("--in-csv", required=True, help="Path to UTF-8 CSV with geom_type and WKT columns.")
    parser.add_argument("--out-folder", required=True, help="Folder for the output GeoPackage.")
    parser.add_argument("--gpkg-name", required=True, help="GeoPackage file name, for example demo.gpkg.")
    parser.add_argument(
        "--feature-basename",
        default="imported",
        help="Base name for output feature class(es); suffixes are added when multiple geometry kinds are present.",
    )
    parser.add_argument("--sr-wkid", type=int, default=4326, help="Spatial reference WKID for WKT parsing, default 4326.")
    args = parser.parse_args()

    try:
        os.environ[DIRECT_RUN_ENV] = "1"
        arcpy.ImportToolbox(str(Path(__file__).resolve()), TOOLBOX_ALIAS)
        arcpy.CsvToGeoPackageTool_csv2gpkg(
            args.in_csv,
            args.out_folder,
            args.gpkg_name,
            args.feature_basename,
            args.sr_wkid,
        )
        raise SystemExit(0)
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        raise SystemExit(1)
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        raise SystemExit(1)
    finally:
        os.environ.pop(DIRECT_RUN_ENV, None)
