# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import arcpy


TOOLBOX_ALIAS = "buf_clip"
DIRECT_RUN_ENV = "BUFFER_CLIP_PYT_DIRECT_RUN"


class Toolbox(object):
    def __init__(self) -> None:
        self.label = "Buffer And Clip"
        self.alias = TOOLBOX_ALIAS
        self.tools = [BufferClipTool]


class BufferClipTool(object):
    def __init__(self) -> None:
        self.label = "Buffer And Clip"
        self.description = "Buffer input points then clip to a polygon boundary."
        self.canRunInBackground = False

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        in_points = arcpy.Parameter(
            displayName="Input Points",
            name="in_points",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
        )
        clip_polygon = arcpy.Parameter(
            displayName="Clip Polygon",
            name="clip_polygon",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
        )
        buffer_distance = arcpy.Parameter(
            displayName="Buffer Distance",
            name="buffer_distance",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        out_buffer = arcpy.Parameter(
            displayName="Buffer Output",
            name="out_buffer",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output",
        )
        out_clip = arcpy.Parameter(
            displayName="Clip Output",
            name="out_clip",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output",
        )
        return [in_points, clip_polygon, buffer_distance, out_buffer, out_clip]

    def execute(self, parameters: list[arcpy.Parameter], messages: object) -> None:
        in_points = parameters[0].valueAsText
        clip_polygon = parameters[1].valueAsText
        buffer_distance = parameters[2].valueAsText
        out_buffer = parameters[3].valueAsText
        out_clip = parameters[4].valueAsText

        for path, label in (
            (in_points, "input points"),
            (clip_polygon, "clip polygon"),
        ):
            if not arcpy.Exists(path):
                raise ValueError(f"{label} not found: {path}")

        arcpy.analysis.Buffer(in_points, out_buffer, buffer_distance, dissolve_option="ALL")
        arcpy.analysis.Clip(out_buffer, clip_polygon, out_clip)
        messages.addMessage(f"Buffer: {out_buffer}")
        messages.addMessage(f"Clip: {out_clip}")


if (
    Path(sys.argv[0]).resolve() == Path(__file__).resolve()
    and os.environ.get(DIRECT_RUN_ENV) != "1"
):
    parser = argparse.ArgumentParser(description="Run buffer and clip from the command line.")
    parser.add_argument("--in-points", required=True)
    parser.add_argument("--clip-polygon", required=True)
    parser.add_argument("--buffer-distance", required=True)
    parser.add_argument("--out-buffer", required=True)
    parser.add_argument("--out-clip", required=True)
    args = parser.parse_args()

    try:
        os.environ[DIRECT_RUN_ENV] = "1"
        arcpy.ImportToolbox(str(Path(__file__).resolve()), TOOLBOX_ALIAS)
        arcpy.BufferClipTool_buf_clip(
            args.in_points,
            args.clip_polygon,
            args.buffer_distance,
            args.out_buffer,
            args.out_clip,
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
