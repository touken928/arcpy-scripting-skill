# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import arcpy


TOOLBOX_ALIAS = "batch_prj"
DIRECT_RUN_ENV = "BATCH_PROJECT_PYT_DIRECT_RUN"


class Toolbox:
    def __init__(self) -> None:
        self.label = "Batch Project"
        self.alias = TOOLBOX_ALIAS
        self.tools = [BatchProjectTool]


class BatchProjectTool:
    def __init__(self) -> None:
        self.label = "Batch Project Feature Classes"
        self.description = "Project all feature classes from an input workspace to an output workspace."
        self.canRunInBackground = False

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        in_workspace = arcpy.Parameter(
            displayName="Input Workspace",
            name="in_workspace",
            datatype="DEWorkspace",
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
        target_wkid = arcpy.Parameter(
            displayName="Target WKID",
            name="target_wkid",
            datatype="GPLong",
            parameterType="Required",
            direction="Input",
        )
        suffix = arcpy.Parameter(
            displayName="Output Suffix",
            name="suffix",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        return [in_workspace, out_workspace, target_wkid, suffix]

    def execute(self, parameters: list[arcpy.Parameter], messages: object) -> None:
        in_workspace = parameters[0].valueAsText
        out_workspace = parameters[1].valueAsText
        target_wkid = int(parameters[2].valueAsText)
        suffix = parameters[3].valueAsText

        if not arcpy.Exists(in_workspace):
            raise ValueError(f"Input workspace not found: {in_workspace}")
        if not arcpy.Exists(out_workspace):
            raise ValueError(f"Output workspace not found: {out_workspace}")

        sr = arcpy.SpatialReference(target_wkid)
        arcpy.env.workspace = in_workspace
        fcs = arcpy.ListFeatureClasses()
        if not fcs:
            messages.addMessage("No feature classes found in input workspace.")
            return

        for fc in fcs:
            out_fc = f"{out_workspace}/{fc}{suffix}"
            if arcpy.Exists(out_fc):
                arcpy.management.Delete(out_fc)
            arcpy.management.Project(fc, out_fc, sr)
            messages.addMessage(f"Projected: {fc} -> {out_fc}")


if (
    Path(sys.argv[0]).resolve() == Path(__file__).resolve()
    and os.environ.get(DIRECT_RUN_ENV) != "1"
):
    parser = argparse.ArgumentParser(description="Run batch project from the command line.")
    parser.add_argument("--in-workspace", required=True)
    parser.add_argument("--out-workspace", required=True)
    parser.add_argument("--wkid", type=int, required=True)
    parser.add_argument("--suffix", required=True)
    args = parser.parse_args()

    try:
        os.environ[DIRECT_RUN_ENV] = "1"
        arcpy.ImportToolbox(str(Path(__file__).resolve()), TOOLBOX_ALIAS)
        arcpy.BatchProjectTool_batch_prj(
            args.in_workspace,
            args.out_workspace,
            str(args.wkid),
            args.suffix,
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
