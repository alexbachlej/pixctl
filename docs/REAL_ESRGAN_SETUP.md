# Real-ESRGAN Setup

pixctl does **not** ship Real-ESRGAN binaries, model weights, or any Python AI dependencies. You must install a backend separately. The Compress / Resize tab works without any backend; only the Upscale tab requires one.

---

## Supported Detection Paths

At startup, pixctl probes for a backend in this priority order:

| Priority | Path checked | Backend kind |
|----------|--------------|--------------|
| 0 | UI path field (user-supplied path) | auto (`.py` → Python, otherwise ncnn) |
| 1 | `$REAL_ESRGAN_PATH` environment variable (when set) | auto (`.py` → Python, otherwise ncnn) |
| 2 | `realesrgan-ncnn-vulkan` in `$PATH` | ncnn-vulkan binary |
| 3 | `./realesrgan-ncnn-vulkan` (project root) | ncnn-vulkan binary |
| 4 | `./Real-ESRGAN/realesrgan-ncnn-vulkan` | ncnn-vulkan binary |
| 5 | `./Real-ESRGAN/inference_realesrgan.py` | Python script |

The first match wins. If none is found, the Upscale tab loads but the Run button is disabled and the header badge reads **No backend**.

### REAL_ESRGAN_PATH override

Set this environment variable to point directly at a binary or script to skip auto-detection:

```bash
# ncnn binary
REAL_ESRGAN_PATH=/opt/realesrgan/realesrgan-ncnn-vulkan pixctl

# Python script
REAL_ESRGAN_PATH=/opt/realesrgan/inference_realesrgan.py pixctl
```

If the path does not exist, a warning is printed to the terminal and auto-detection continues normally.

### Venv detection for the Python script backend

When `./Real-ESRGAN/inference_realesrgan.py` is selected (priority 5), pixctl looks for a virtual environment at `./Real-ESRGAN/.venv/bin/python` and uses it automatically. If the venv is absent, the system Python interpreter is used and a warning is printed to the terminal.

---

## Option A — ncnn-vulkan Binary

The `realesrgan-ncnn-vulkan` binary uses Vulkan for GPU acceleration. It is the fastest option and has no Python dependencies beyond what pixctl already installs.

**Steps:**

1. Download a pre-built release from the upstream ncnn-vulkan project (search for `realesrgan-ncnn-vulkan` releases on GitHub).
2. Extract the archive. It contains the binary and model files (`.bin`/`.param`).
3. Place the binary in one of the detected paths:
   - In your system `$PATH` (e.g. `/usr/local/bin/`), or
   - Next to the pixctl project root as `./realesrgan-ncnn-vulkan`, or
   - Under `./Real-ESRGAN/realesrgan-ncnn-vulkan`
4. Ensure the binary is executable: `chmod +x realesrgan-ncnn-vulkan`
5. Keep the model files in the same directory as the binary — the binary expects to find them there.
6. Restart pixctl (`./start.sh`). The header badge should update to show the detected backend.

**Face enhancement:** not supported by the ncnn-vulkan binary. If the Face Enhancement option is checked when this backend is active, it is silently ignored and upscaling proceeds without it.

---

## Option B — Python Script (inference_realesrgan.py)

The Python script backend uses PyTorch. It supports face enhancement via GFPGAN but requires additional dependencies installed separately.

**Steps:**

**Option B1 — Next to the pixctl project root:**

1. Clone or download the Real-ESRGAN Python repository so that the project root contains a directory named `Real-ESRGAN`:

   ```
   pixctl/
     Real-ESRGAN/
       inference_realesrgan.py
       ...
   ```

2. Follow the Real-ESRGAN Python project's own installation instructions to install its Python dependencies (typically `torch`, `basicsr`, `facexlib`, `gfpgan`, etc.). These are not managed by pixctl's `requirements.txt`.

3. Restart pixctl. If `./Real-ESRGAN/inference_realesrgan.py` is found, the backend is detected and face enhancement becomes available.

---

## ncnn-vulkan vs Python Backend

| | ncnn-vulkan binary | Python script |
|---|---|---|
| Speed | Generally faster (Vulkan GPU) | Slower (depends on PyTorch/CUDA setup) |
| Dependencies | None beyond the binary and models | PyTorch + multiple packages |
| Face enhancement | No | Yes (via GFPGAN) |
| GPU requirement | Vulkan-capable GPU | CUDA GPU recommended; CPU possible but slow |
| Platform | Linux, macOS, Windows | Linux, macOS, Windows |

---

## Face Enhancement Support Limits

Face enhancement is only available when the **Python script backend** (`inference_realesrgan.py`) is detected. It is not supported by any of the ncnn-vulkan binary paths.

If Face Enhancement is checked but the active backend is ncnn-vulkan, pixctl silently proceeds without face enhancement and logs a warning to the terminal. No error is shown in the UI.

Face enhancement quality and behavior depend on the GFPGAN version bundled with the Real-ESRGAN Python project, not on pixctl.
