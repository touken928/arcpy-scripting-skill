from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import run_example

arcpy = pytest.importorskip("arcpy")


def test_buffer_and_clip_features_runs_and_generates_outputs(tmp_path: Path) -> None:
    proc = run_example("buffer_and_clip_features.py", tmp_path)
    assert proc.returncode == 0, proc.stderr or proc.stdout

    out_buffer = f"{tmp_path}/buffer_clip_demo.gdb/buffer_result"
    out_clip = f"{tmp_path}/buffer_clip_demo.gdb/clip_result"

    assert arcpy.Exists(out_buffer), f"Buffer output missing: {out_buffer}"
    assert arcpy.Exists(out_clip), f"Clip output missing: {out_clip}"
    assert int(arcpy.management.GetCount(out_buffer)[0]) > 0
    assert int(arcpy.management.GetCount(out_clip)[0]) > 0
