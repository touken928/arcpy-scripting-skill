# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import arcpy


TOOLBOX_ALIAS = "sample_count"
DIRECT_RUN_ENV = "SAMPLE_COUNT_TOOLBOX_DIRECT_RUN"


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
        in_features = parameters[0].valueAsText
        if not arcpy.Exists(in_features):
            raise ValueError(f"Input features not found: {in_features}")

        count = int(arcpy.management.GetCount(in_features)[0])
        messages.addMessage(f"Feature count: {count}")
        parameters[1].value = count


if (
    Path(sys.argv[0]).resolve() == Path(__file__).resolve()
    and os.environ.get(DIRECT_RUN_ENV) != "1"
):
    parser = argparse.ArgumentParser(
        description="Run the Count Features Python toolbox from the command line."
    )
    parser.add_argument(
        "--in-features",
        required=True,
        help="Existing feature class or feature layer to count.",
    )
    args = parser.parse_args()

    try:
        os.environ[DIRECT_RUN_ENV] = "1"
        arcpy.ImportToolbox(str(Path(__file__).resolve()), TOOLBOX_ALIAS)
        result = arcpy.CountFeaturesTool_sample_count(args.in_features)
        print(f"Input features: {args.in_features}")
        print(f"Feature count: {result.getOutput(0)}")
        raise SystemExit(0)
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        raise SystemExit(1)
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        raise SystemExit(1)
    finally:
        os.environ.pop(DIRECT_RUN_ENV, None)
