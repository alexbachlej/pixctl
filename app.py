import os
import time

from src.config import HOST, init_dirs, resolve_port
from src.realesrgan_runner import detect_backend
from src.ui import CUSTOM_CSS, THEME, build_ui

if __name__ == "__main__":
    t0 = time.monotonic()
    init_dirs()

    port, fallback, requested = resolve_port()
    backend = detect_backend(None)

    if backend.available:
        kind = "ncnn-vulkan" if backend.kind == "ncnn" else "Python script"
        backend_line = f"OK  [{kind}]  {backend.path}"
    else:
        backend_line = "no upscale backend  (compression still works)"

    demo = build_ui()
    demo.queue()
    elapsed = time.monotonic() - t0

    print()
    print("Starting pixctl...")
    print(f"Backend:  {backend_line}")
    if fallback:
        print(f"Port {requested} busy — falling back to {port}")
    print(f"Ready in  {elapsed:.1f}s")
    print()
    print("pixctl running at:")
    print(f"  http://{HOST}:{port}")
    print()

    inbrowser = os.environ.get("PIXCTL_OPEN_BROWSER", "1") != "0"
    demo.launch(
        server_name=HOST,
        server_port=port,
        quiet=True,
        inbrowser=inbrowser,
        theme=THEME,
        css=CUSTOM_CSS,
    )
