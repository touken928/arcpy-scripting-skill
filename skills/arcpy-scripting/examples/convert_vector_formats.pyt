# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import arcpy


TOOLBOX_ALIAS = "vec_fmt"
DIRECT_RUN_ENV = "CONVERT_VECTOR_FORMATS_PYT_DIRECT_RUN"


class Toolbox(object):
    def __init__(self) -> None:
        self.label = "Convert Vector Formats"
        self.alias = TOOLBOX_ALIAS
        self.tools = [
            ExportShapefileTool,
            CopyToWorkspaceTool,
            ExportGeoPackageTool,
            ExportGeoJsonTool,
            ShapefileToWorkspaceTool,
        ]


class ExportShapefileTool(object):
    def __init__(self) -> None:
        self.label = "Export To Shapefile"
        self.description = "Export input features to a shapefile."
        self.canRunInBackground = False

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        in_fc = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
        )
        out_shp = arcpy.Parameter(
            displayName="Output Shapefile",
            name="out_shp",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Output",
        )
        return [in_fc, out_shp]

    def execute(self, parameters: list[arcpy.Parameter], messages: object) -> None:
        in_fc = parameters[0].valueAsText
        out_shp = parameters[1].valueAsText
        if not arcpy.Exists(in_fc):
            raise ValueError(f"Input features not found: {in_fc}")
        if arcpy.Exists(out_shp):
            arcpy.management.Delete(out_shp)
        arcpy.conversion.ExportFeatures(in_fc, out_shp)
        messages.addMessage(f"Shapefile: {out_shp}")


class CopyToWorkspaceTool(object):
    def __init__(self) -> None:
        self.label = "Copy To Workspace"
        self.description = "Copy features to another workspace using FeatureClassToFeatureClass."
        self.canRunInBackground = False

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        in_fc = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
        )
        out_workspace = arcpy.Parameter(
            displayName="Output Workspace",
            name="out_workspace",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        out_name = arcpy.Parameter(
            displayName="Output Name",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        return [in_fc, out_workspace, out_name]

    def execute(self, parameters: list[arcpy.Parameter], messages: object) -> None:
        in_fc = parameters[0].valueAsText
        out_workspace = parameters[1].valueAsText
        out_name = parameters[2].valueAsText
        if not arcpy.Exists(in_fc):
            raise ValueError(f"Input features not found: {in_fc}")
        if not arcpy.Exists(out_workspace):
            raise ValueError(f"Output workspace not found: {out_workspace}")
        out_path = f"{out_workspace}/{out_name}"
        if arcpy.Exists(out_path):
            arcpy.management.Delete(out_path)
        arcpy.conversion.FeatureClassToFeatureClass(in_fc, out_workspace, out_name)
        messages.addMessage(f"Copied: {out_path}")


class ExportGeoPackageTool(object):
    def __init__(self) -> None:
        self.label = "Export To GeoPackage Layer"
        self.description = "Export features into a GeoPackage feature class path."
        self.canRunInBackground = False

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        in_fc = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
        )
        out_gpkg_layer = arcpy.Parameter(
            displayName="Output GeoPackage Layer",
            name="out_gpkg_layer",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output",
        )
        return [in_fc, out_gpkg_layer]

    def execute(self, parameters: list[arcpy.Parameter], messages: object) -> None:
        in_fc = parameters[0].valueAsText
        out_layer = parameters[1].valueAsText
        if not arcpy.Exists(in_fc):
            raise ValueError(f"Input features not found: {in_fc}")
        gpkg_path = str(Path(out_layer).parents[0])
        if not arcpy.Exists(gpkg_path):
            arcpy.management.CreateSQLiteDatabase(gpkg_path, "GEOPACKAGE")
        if arcpy.Exists(out_layer):
            arcpy.management.Delete(out_layer)
        arcpy.conversion.ExportFeatures(in_fc, out_layer)
        messages.addMessage(f"GeoPackage layer: {out_layer}")


class ExportGeoJsonTool(object):
    def __init__(self) -> None:
        self.label = "Export To GeoJSON"
        self.description = "Export features to a GeoJSON file using FeaturesToJSON."
        self.canRunInBackground = False

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        in_fc = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
        )
        out_geojson = arcpy.Parameter(
            displayName="Output GeoJSON",
            name="out_geojson",
            datatype="DEFile",
            parameterType="Required",
            direction="Output",
        )
        return [in_fc, out_geojson]

    def execute(self, parameters: list[arcpy.Parameter], messages: object) -> None:
        in_fc = parameters[0].valueAsText
        out_geojson = Path(parameters[1].valueAsText)
        if not arcpy.Exists(in_fc):
            raise ValueError(f"Input features not found: {in_fc}")
        if out_geojson.exists():
            out_geojson.unlink()
        arcpy.conversion.FeaturesToJSON(
            in_fc,
            str(out_geojson),
            "NOT_FORMATTED",
            "NO_Z_VALUES",
            "NO_M_VALUES",
            "GEOJSON",
            "KEEP_INPUT_SR",
        )
        messages.addMessage(f"GeoJSON: {out_geojson}")


class ShapefileToWorkspaceTool(object):
    def __init__(self) -> None:
        self.label = "Shapefile To Workspace"
        self.description = "Import a shapefile into a workspace as a new feature class."
        self.canRunInBackground = False

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        in_shp = arcpy.Parameter(
            displayName="Input Shapefile",
            name="in_shp",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input",
        )
        out_workspace = arcpy.Parameter(
            displayName="Output Workspace",
            name="out_workspace",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        out_name = arcpy.Parameter(
            displayName="Output Name",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        return [in_shp, out_workspace, out_name]

    def execute(self, parameters: list[arcpy.Parameter], messages: object) -> None:
        in_shp = parameters[0].valueAsText
        out_workspace = parameters[1].valueAsText
        out_name = parameters[2].valueAsText
        if not arcpy.Exists(in_shp):
            raise ValueError(f"Input shapefile not found: {in_shp}")
        if not arcpy.Exists(out_workspace):
            raise ValueError(f"Output workspace not found: {out_workspace}")
        out_path = f"{out_workspace}/{out_name}"
        if arcpy.Exists(out_path):
            arcpy.management.Delete(out_path)
        arcpy.conversion.FeatureClassToFeatureClass(in_shp, out_workspace, out_name)
        messages.addMessage(f"Imported shapefile: {out_path}")


if (
    Path(sys.argv[0]).resolve() == Path(__file__).resolve()
    and os.environ.get(DIRECT_RUN_ENV) != "1"
):
    parser = argparse.ArgumentParser(description="Run one vector conversion tool from the command line.")
    parser.add_argument(
        "--tool",
        required=True,
        choices=["shapefile", "copy_gdb", "gpkg", "geojson", "shp_to_ws"],
    )
    parser.add_argument("--in-features", help="Input feature class or layer path.")
    parser.add_argument("--out-shp", help="Output shapefile path for --tool shapefile.")
    parser.add_argument("--out-workspace", help="Output workspace for copy or shp_to_ws.")
    parser.add_argument("--out-name", help="Output feature class name for copy or shp_to_ws.")
    parser.add_argument("--out-gpkg-layer", help="Output GeoPackage layer path for --tool gpkg.")
    parser.add_argument("--out-geojson", help="Output GeoJSON file path for --tool geojson.")
    parser.add_argument("--in-shp", help="Input shapefile for --tool shp_to_ws.")
    args = parser.parse_args()

    try:
        os.environ[DIRECT_RUN_ENV] = "1"
        arcpy.ImportToolbox(str(Path(__file__).resolve()), TOOLBOX_ALIAS)
        if args.tool == "shapefile":
            if not args.in_features or not args.out_shp:
                raise ValueError("--in-features and --out-shp are required for shapefile export.")
            arcpy.ExportShapefileTool_vec_fmt(args.in_features, args.out_shp)
        elif args.tool == "copy_gdb":
            if not args.in_features or not args.out_workspace or not args.out_name:
                raise ValueError("--in-features, --out-workspace, and --out-name are required for copy_gdb.")
            arcpy.CopyToWorkspaceTool_vec_fmt(args.in_features, args.out_workspace, args.out_name)
        elif args.tool == "gpkg":
            if not args.in_features or not args.out_gpkg_layer:
                raise ValueError("--in-features and --out-gpkg-layer are required for gpkg export.")
            arcpy.ExportGeoPackageTool_vec_fmt(args.in_features, args.out_gpkg_layer)
        elif args.tool == "geojson":
            if not args.in_features or not args.out_geojson:
                raise ValueError("--in-features and --out-geojson are required for geojson export.")
            arcpy.ExportGeoJsonTool_vec_fmt(args.in_features, args.out_geojson)
        elif args.tool == "shp_to_ws":
            if not args.in_shp or not args.out_workspace or not args.out_name:
                raise ValueError("--in-shp, --out-workspace, and --out-name are required for shp_to_ws.")
            arcpy.ShapefileToWorkspaceTool_vec_fmt(args.in_shp, args.out_workspace, args.out_name)
        raise SystemExit(0)
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        raise SystemExit(1)
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        raise SystemExit(1)
    finally:
        os.environ.pop(DIRECT_RUN_ENV, None)
