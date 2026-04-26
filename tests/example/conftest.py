from __future__ import annotations

import subprocess
import sys
from typing import Sequence
from pathlib import Path

import pytest

arcpy = pytest.importorskip("arcpy")

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "skills" / "arcpy-scripting" / "examples"


def run_example(
    script_name: str,
    extra_args: Sequence[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    script = EXAMPLES_DIR / script_name
    assert script.exists(), f"Example script not found: {script}"
    cmd = [sys.executable, str(script)]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
