from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import arcpy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open an existing APRX and save a modified copy."
    )
    parser.add_argument(
        "--in-aprx",
        required=True,
        help="Path to an existing .aprx project created in ArcGIS Pro.",
    )
    parser.add_argument(
        "--out-folder",
        default=str(Path.cwd() / "examples_output"),
        help="Output parent folder path (default: ./examples_output).",
    )
    return parser.parse_args()


def prepare_base_project(in_aprx: Path, out_folder: Path) -> Path:
    base_aprx = out_folder / "base_project.aprx"
    if base_aprx.exists():
        base_aprx.unlink()
    if not in_aprx.exists():
        raise FileNotFoundError(f"Input APRX not found: {in_aprx}")
    shutil.copy2(in_aprx, base_aprx)
    return base_aprx


def main() -> int:
    args = parse_args()
    arcpy.env.overwriteOutput = True

    try:
        out_folder = Path(args.out_folder).expanduser().resolve()
        out_folder.mkdir(parents=True, exist_ok=True)
        in_aprx = Path(args.in_aprx).expanduser().resolve()

        base_aprx = prepare_base_project(in_aprx, out_folder)
        aprx = arcpy.mp.ArcGISProject(str(base_aprx))
        maps = aprx.listMaps()
        layouts = aprx.listLayouts()

        modified_aprx = out_folder / "modified_project.aprx"
        aprx.saveACopy(str(modified_aprx))

        print(f"Base APRX: {base_aprx}")
        print(f"Modified APRX: {modified_aprx}")
        print(f"Map count: {len(maps)}")
        print(f"Layout count: {len(layouts)}")
        return 0
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        return 1
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
