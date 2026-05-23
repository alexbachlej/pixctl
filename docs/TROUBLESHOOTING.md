# Troubleshooting

Common problems and fixes for pixctl.

---

## Port Already in Use

**pixctl now handles port conflicts automatically.** If port 7860 is busy, it tries 7861, 7862, … and prints the URL it actually bound to:

```
Port 7860 busy — falling back to 7861
pixctl running at:
  http://127.0.0.1:7861
```

You only need to act if all ports in the scan range (7860–7879) are occupied, or if you want to lock a specific port.

### Force a specific port

Set `PIXCTL_PORT` (or the lower-priority `GRADIO_SERVER_PORT`) before running:

```bash
PIXCTL_PORT=8080 pixctl
PIXCTL_PORT=8080 ./start.sh
```

The fallback scan still applies from whatever port you specify.

### Find and kill the conflicting process manually

```bash
# Find the process using port 7860
lsof -i :7860
# or
ss -tlnp | grep 7860

# Stop it by PID
kill <PID>
```

### No free port found (all ports 7860–7879 busy)

**Symptom:**

```
OSError: No free port found in range 7860–7879. Stop other services or set PIXCTL_PORT to a free port.
```

**Fix:** Either stop one of the conflicting services, or start pixctl on a different base port:

```bash
PIXCTL_PORT=8080 pixctl
```

---

## Dependency Install Fails

**Symptom:** `pip install -r requirements.txt` exits with an error during `./start.sh`.

**Common causes and fixes:**

| Symptom detail | Fix |
|----------------|-----|
| Network error / timeout | Check internet connection and retry `./start.sh` |
| Build error, compiler missing | Ensure Python 3.9+ development headers are present (`sudo apt install python3-dev` on Debian/Ubuntu) |
| `ERROR: python3 not found` | Install Python 3.9+ via your OS package manager |
| Corrupt venv from a previous failed install | `rm -rf .venv && ./start.sh` |

---

## Real-ESRGAN Not Detected

**Symptom:** The Upscale tab loads but the Run button is disabled. The header badge reads **No backend** or similar.

**Fix:**

1. Confirm you have installed a backend. See [REAL_ESRGAN_SETUP.md](REAL_ESRGAN_SETUP.md).
2. Check that the binary or script is at one of the auto-detected paths (in order):
   - `$REAL_ESRGAN_PATH` env var (highest priority — overrides all auto-detected paths)
   - `realesrgan-ncnn-vulkan` in `$PATH`
   - `./realesrgan-ncnn-vulkan`
   - `./Real-ESRGAN/realesrgan-ncnn-vulkan`
   - `./Real-ESRGAN/inference_realesrgan.py`
3. If using the binary, confirm it is executable: `ls -l realesrgan-ncnn-vulkan` should show `x` bits.
4. Restart pixctl — backend detection runs at startup only.

If upscale fails mid-run with `Backend executable not found`, the binary was moved or removed after the app started. Restore it to its expected location and restart.

---

## Image File Too Large

**Symptom:** Loading a large image is slow, causes a memory error, or crashes the app.

**Notes:**

- pixctl has no hard file size limit enforced in the UI, but very large images (e.g. multi-hundred-megapixel TIFFs) can exhaust available RAM.
- For upscaling, the backend process also needs enough memory to handle the full image.
- Gradio's file upload component may impose its own size limits depending on version.

**Fix:** Pre-resize the image before processing, or use the Compress / Resize tab to downsample it first.

---

## Output Files Too Large

**Symptom:** After compression, the output file is larger than the target size specified.

**Explanation:** The iterative compressor reduces quality in steps of 5 and then progressively downsamples the image. If the target is extremely aggressive (e.g. compressing a 10 MP photo to under 100 KB), the process will eventually reach the minimum achievable size (pixel width of 1) and save at that point with a log message:

```
Cannot meet target; saved at minimum achievable size
```

or, if the image is being resized below 800 px:

```
Warning: resizing below 800 px (width=NNN) to satisfy target
```

**Fix:** Use a more realistic target size for the input image, or accept the minimum achievable output.

Note: PNG output does not support quality-based compression. Target file size for PNG is enforced via downsampling only.

---

## Permissions Issue

**Symptom:** `./start.sh` fails with `Permission denied`.

**Fix:** Ensure the script is executable:

```bash
chmod +x start.sh
./start.sh
```

If outputs or temp directories cannot be written to, check that the project directory is writable by your user:

```bash
ls -ld outputs/ temp/
```

---

## Browser Does Not Open Automatically

**Symptom:** `./start.sh` runs and the app starts, but no browser window opens.

**Explanation:** Gradio attempts to open the default browser automatically, but this may fail in headless environments, SSH sessions, or when no default browser is configured.

**Fix:** Open the URL manually. pixctl always prints the URL at startup:

```
pixctl running at:
  http://127.0.0.1:7860
```

Copy and paste that URL into your browser.

**To suppress auto-open intentionally** (useful in SSH or server contexts):

```bash
PIXCTL_OPEN_BROWSER=0 pixctl
PIXCTL_OPEN_BROWSER=0 ./start.sh
```

---

## Gradio Launches but UI Is Unavailable

**Symptom:** The terminal shows the Gradio URL and no errors, but opening the URL in the browser shows a blank page, a connection refused error, or an endless loading spinner.

**Possible causes:**

- **Wrong URL:** The app binds to `127.0.0.1:7860`. Make sure you are accessing it from the same machine. It is not accessible from other machines on the network by design.
- **Firewall or proxy:** A local firewall rule or browser proxy may be blocking `127.0.0.1`. Disable the proxy for local addresses.
- **Gradio still starting up:** Gradio can take a second or two to be ready after printing the URL. Wait a moment and refresh.
- **Port conflict:** Another process grabbed 7860 between app start and the browser request. Check with `lsof -i :7860` and see the [Port Already in Use](#port-already-in-use) section.
- **Crash after startup:** Scroll the terminal for a Python traceback. If the app crashed immediately after printing the URL, restart with `./start.sh` and read the full output.

---

## Enabling Debug Output

By default pixctl produces no diagnostic terminal output. To turn on verbose logging — backend detection details, the exact subprocess command, working directory, stdout/stderr, and output-file detection — set the `PIXCTL_DEBUG` environment variable to `1` before starting the app:

```bash
PIXCTL_DEBUG=1 ./start.sh
# or, if running manually:
PIXCTL_DEBUG=1 python app.py
```

With `PIXCTL_DEBUG=1` set, the terminal will print backend source, type, path, Python executable, and full inference command for every upscale run. All result data (command, cwd, stdout/stderr, output path) is always included in the in-app log regardless of this flag — `PIXCTL_DEBUG=1` adds the extra terminal mirror only.

---

## Real-ESRGAN Inference Failures

This section covers failures that occur after a backend is detected — the Run button is enabled, but the upscale job fails or produces no output.

Enable debug terminal output with `PIXCTL_DEBUG=1` (see above) to see `DEBUG:` lines showing exactly what was launched and what it returned.

### Backend detected but inference fails (`UnboundLocalError`, wrong args)

**Symptom:** The upscale job completes quickly with an error, or the output file is missing. The terminal shows a Python traceback containing `UnboundLocalError` or an argument error.

**What to look for:**

```
DEBUG: backend kind='python' path=/path/to/inference_realesrgan.py
DEBUG: command=['/path/to/python', '/path/to/inference_realesrgan.py', '-n', 'RealESRGAN_x4plus', ...]
DEBUG: returncode=1
DEBUG: stderr='...'
```

**Common causes and fixes:**

| Cause | Fix |
|-------|-----|
| `UnboundLocalError` inside `inference_realesrgan.py` | The script version is incompatible. Update Real-ESRGAN: `cd Real-ESRGAN && git pull`. |
| Returncode 1 with no useful stderr | Run the command from `DEBUG: command=` manually in a terminal to see full output. |
| `TypeError: argument ... expected str, not PosixPath` | Upgrade Real-ESRGAN or report the path type mismatch as a bug. |

---

### Invalid model names

**Symptom:** Inference exits immediately. `DEBUG: stderr=` shows something like:

```
FileNotFoundError: [Errno 2] No such file or directory: '.../weights/UnknownModel.pth'
```

or

```
KeyError: 'UnknownModel'
```

**What happened:** The model name passed via `-n` did not match any known Real-ESRGAN model. pixctl maps its internal model IDs (e.g. `realesrgan-x4plus`) to script names (e.g. `RealESRGAN_x4plus`) — but if you pass a custom value via the UI or code, it is forwarded as-is.

**Fix:** Use one of the supported model IDs listed in the Upscale tab. Valid internal IDs:

- `realesrgan-x4plus`
- `realesrgan-x4plus-anime`
- `realesr-animevideov3`

If you need a custom model, place its `.pth` weights in the `weights/` directory of your Real-ESRGAN install and use the exact filename stem as the model name.

---

### Invalid CLI arguments

**Symptom:** `DEBUG: returncode=2` and `DEBUG: stderr=` contains a usage/argument error like:

```
error: unrecognized arguments: --face_enhance
usage: inference_realesrgan.py [-h] ...
```

or for the ncnn binary:

```
invalid option -- 'x'
```

**Fix:**

1. Copy the full command from `DEBUG: command=` and run it manually to see the complete error.
2. For the Python backend: your `inference_realesrgan.py` version may not support all flags pixctl passes (e.g. `--fp32`, `--suffix`). Update Real-ESRGAN to a recent commit.
3. For the ncnn binary: ensure you have a recent release that supports `-n` (model name) and `-s` (scale) flags.

---

### Python backend venv issues

**Symptom:** `DEBUG: stderr=` contains import errors such as:

```
ModuleNotFoundError: No module named 'basicsr'
ModuleNotFoundError: No module named 'torch'
```

or:

```
DEBUG: python_exe=/usr/bin/python3
```
(system Python used instead of the Real-ESRGAN venv)

**Cause:** The Python executable used to run `inference_realesrgan.py` does not have the required packages installed. This happens when:

- The Real-ESRGAN venv does not exist at the expected path (`Real-ESRGAN/.venv/`)
- The venv was created but packages were not installed
- A `REAL_ESRGAN_PATH` override points to the script but the associated interpreter is wrong

**Fix:**

1. Create and populate the Real-ESRGAN venv:
   ```bash
   cd /path/to/Real-ESRGAN
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Confirm the venv python is being used — `DEBUG: python_exe=` should show `.venv/bin/python`.
3. If the wrong interpreter is used, set `REAL_ESRGAN_PATH` to the `.py` script *and* ensure the venv exists at `Real-ESRGAN/.venv/` (pixctl looks there automatically).
4. If packages are present but still fail to import, the venv may be broken. Recreate it:
   ```bash
   rm -rf Real-ESRGAN/.venv
   python3 -m venv Real-ESRGAN/.venv
   Real-ESRGAN/.venv/bin/pip install -r Real-ESRGAN/requirements.txt
   ```
