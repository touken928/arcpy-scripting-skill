# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import arcpy


TOOLBOX_ALIAS = "sel_export"
DIRECT_RUN_ENV = "SELECT_EXPORT_PYT_DIRECT_RUN"


class Toolbox(object):
    def __init__(self) -> None:
        self.label = "Select And Export"
        self.alias = TOOLBOX_ALIAS
        self.tools = [SelectExportTool]


class SelectExportTool(object):
    def __init__(self) -> None:
        self.label = "Select And Export"
        self.description = "Select features by attribute and export to a new feature class."
        self.canRunInBackground = False

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        in_features = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
        )
        where_clause = arcpy.Parameter(
            displayName="Where Clause",
            name="where_clause",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        layer_name = arcpy.Parameter(
            displayName="Temporary Layer Name",
            name="layer_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        out_features = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output",
        )
        return [in_features, where_clause, layer_name, out_features]

    def execute(self, parameters: list[arcpy.Parameter], messages: object) -> None:
        in_features = parameters[0].valueAsText
        where_clause = parameters[1].valueAsText
        layer_name = parameters[2].valueAsText
        out_features = parameters[3].valueAsText

        if not arcpy.Exists(in_features):
            raise ValueError(f"Input features not found: {in_features}")

        layer = arcpy.management.MakeFeatureLayer(in_features, layer_name)[0]
        arcpy.management.SelectLayerByAttribute(layer, "NEW_SELECTION", where_clause)
        arcpy.conversion.ExportFeatures(layer, out_features)
        messages.addMessage(f"Exported: {out_features}")


if (
    Path(sys.argv[0]).resolve() == Path(__file__).resolve()
    and os.environ.get(DIRECT_RUN_ENV) != "1"
):
    parser = argparse.ArgumentParser(description="Run select and export from the command line.")
    parser.add_argument("--in-features", required=True)
    parser.add_argument("--where", required=True)
    parser.add_argument("--layer-name", required=True)
    parser.add_argument("--out-features", required=True)
    args = parser.parse_args()

    try:
        os.environ[DIRECT_RUN_ENV] = "1"
        arcpy.ImportToolbox(str(Path(__file__).resolve()), TOOLBOX_ALIAS)
        arcpy.SelectExportTool_sel_export(
            args.in_features,
            args.where,
            args.layer_name,
            args.out_features,
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
