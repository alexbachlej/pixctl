import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.config import BASE_DIR


@dataclass
class Backend:
    kind: str          # "ncnn" | "python" | "none"
    path: Path
    available: bool
    supports_face_enhance: bool


@dataclass
class RunResult:
    success: bool
    stdout: str
    stderr: str
    returncode: int
    duration: float
    output_path: Optional[Path] = field(default=None)


def detect_backend() -> Backend:
    """Probe for Real-ESRGAN backends in priority order."""
    # 1. realesrgan-ncnn-vulkan in PATH
    which = shutil.which("realesrgan-ncnn-vulkan")
    if which:
        return Backend(kind="ncnn", path=Path(which), available=True, supports_face_enhance=False)

    # 2. ./realesrgan-ncnn-vulkan (local binary next to project root)
    local_ncnn = BASE_DIR / "realesrgan-ncnn-vulkan"
    if local_ncnn.exists():
        return Backend(kind="ncnn", path=local_ncnn, available=True, supports_face_enhance=False)

    # 3. ./Real-ESRGAN/realesrgan-ncnn-vulkan
    nested_ncnn = BASE_DIR / "Real-ESRGAN" / "realesrgan-ncnn-vulkan"
    if nested_ncnn.exists():
        return Backend(kind="ncnn", path=nested_ncnn, available=True, supports_face_enhance=False)

    # 4. ./Real-ESRGAN/inference_realesrgan.py (Python script backend)
    inference_py = BASE_DIR / "Real-ESRGAN" / "inference_realesrgan.py"
    if inference_py.exists():
        return Backend(kind="python", path=inference_py, available=True, supports_face_enhance=True)

    return Backend(kind="none", path=Path(), available=False, supports_face_enhance=False)


def _build_command(
    backend: Backend,
    input_path: Path,
    output_path: Path,
    model: str,
    scale: int,
    face_enhance: bool,
) -> list:
    if backend.kind == "ncnn":
        return [
            str(backend.path),
            "-i", str(input_path),
            "-o", str(output_path),
            "-n", model,
            "-s", str(scale),
        ]
    if backend.kind == "python":
        # inference_realesrgan.py writes to an output directory, not a file path
        cmd = [
            sys.executable,
            str(backend.path),
            "-n", model,
            "-i", str(input_path),
            "-o", str(output_path.parent),
            "--outscale", str(scale),
        ]
        if face_enhance:
            cmd.append("--face_enhance")
        return cmd
    raise ValueError("No Real-ESRGAN backend available.")


def run_upscale(
    backend: Backend,
    input_path: Path,
    output_path: Path,
    model: str = "realesrgan-x4plus",
    scale: int = 2,
    face_enhance: bool = False,
) -> RunResult:
    """Run upscaling and return a RunResult.

    output_path is the desired full output file path. The caller is responsible
    for ensuring it does not already exist (use safe_output_path).
    """
    if not backend.available:
        return RunResult(
            success=False,
            stdout="",
            stderr="No Real-ESRGAN backend found.",
            returncode=-1,
            duration=0.0,
        )

    if face_enhance and not backend.supports_face_enhance:
        print(
            f"WARNING: face_enhance requested but not supported by '{backend.kind}' "
            "backend — continuing without it."
        )
        face_enhance = False

    cmd = _build_command(backend, input_path, output_path, model, scale, face_enhance)
    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as exc:
        duration = time.monotonic() - t0
        return RunResult(
            success=False,
            stdout="",
            stderr=f"Backend executable not found: {exc}",
            returncode=-1,
            duration=duration,
        )
    duration = time.monotonic() - t0

    # For the python backend the script writes to output_dir/input_filename.
    # Rename it to the caller-specified output_path if they differ.
    if backend.kind == "python" and proc.returncode == 0:
        actual = output_path.parent / input_path.name
        if actual.exists() and actual != output_path:
            actual.rename(output_path)

    success = proc.returncode == 0 and output_path.exists()
    return RunResult(
        success=success,
        stdout=proc.stdout,
        stderr=proc.stderr,
        returncode=proc.returncode,
        duration=duration,
        output_path=output_path if success else None,
    )
