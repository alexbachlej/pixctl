from datetime import datetime
from pathlib import Path


def timestamped_filename(stem: str, suffix: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{stem}_{ts}{suffix}"


def safe_output_path(dest_dir: Path, filename: str) -> Path:
    """Return a path under dest_dir, raising if it would already exist."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / filename
    if out.exists():
        raise FileExistsError(f"Output file already exists: {out}")
    return out


def placeholder_result(operation: str) -> str:
    return f"[{operation}] Not yet implemented."
