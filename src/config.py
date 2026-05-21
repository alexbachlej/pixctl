from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUTS = {
    "upscaled": BASE_DIR / "outputs" / "upscaled",
    "compressed": BASE_DIR / "outputs" / "compressed",
    "batch": BASE_DIR / "outputs" / "batch",
}
TEMP_DIR = BASE_DIR / "temp"

HOST = "127.0.0.1"
PORT = 7860


def init_dirs() -> None:
    for path in OUTPUTS.values():
        path.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
