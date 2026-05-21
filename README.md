# pixctl

Local image processing toolkit with a Gradio web UI. No accounts, no cloud, no telemetry — everything runs on your machine.

Supports AI upscaling via Real-ESRGAN (optional external backend), lossless/lossy compression, format conversion, and metadata stripping.

---

## Features

**Upscale tab** (requires a Real-ESRGAN backend — see [Real-ESRGAN Setup](docs/REAL_ESRGAN_SETUP.md))
- 2× and 4× AI upscaling
- Models: `realesrgan-x4plus`, `realesrgan-x4plus-anime`, `realesr-animevideov3`
- Output formats: PNG, JPEG, WebP
- Optional face enhancement (Python script backend only)
- Optional auto-compress pass after upscaling (quality, max-width, target file size)

**Compress / Resize tab** (no backend required)
- Format conversion: JPEG, PNG, WebP
- Quality slider (1–100 for JPEG/WebP)
- Max-width downsampling presets: 1280, 1920, 2560, 3840 px
- Target file size presets: 1 MB, 2 MB, 5 MB, 10 MB (iterative quality reduction)
- EXIF and metadata stripping

**Batch Folder Mode tab**
- UI skeleton present; full implementation is a work in progress

---

## Screenshots

> Screenshots are not yet included. Placeholder directory: [`docs/screenshots/`](docs/screenshots/)

---

## Quick Start

```bash
git clone <repo-url> pixctl
cd pixctl
./start.sh
```

The app opens at **http://127.0.0.1:7860**.

`start.sh` will:
1. Create `.venv` if it does not exist
2. Install dependencies from `requirements.txt` into the venv
3. Launch the Gradio app

For a more detailed walkthrough see [docs/HOWTO.md](docs/HOWTO.md).

---

## Supported Backends

The Upscale tab requires an external Real-ESRGAN binary or Python script. The app detects backends automatically at startup in this order:

| Priority | Path | Kind | Face enhance |
|----------|------|------|--------------|
| 1 | `realesrgan-ncnn-vulkan` in `$PATH` | ncnn-vulkan binary | No |
| 2 | `./realesrgan-ncnn-vulkan` | ncnn-vulkan binary (local) | No |
| 3 | `./Real-ESRGAN/realesrgan-ncnn-vulkan` | ncnn-vulkan binary (nested) | No |
| 4 | `./Real-ESRGAN/inference_realesrgan.py` | Python script | Yes |

If no backend is found, the Upscale tab loads but the Run button is disabled. The Compress / Resize and Batch tabs are unaffected.

See [docs/REAL_ESRGAN_SETUP.md](docs/REAL_ESRGAN_SETUP.md) for full setup instructions.

---

## Workflow Examples

### Compress an image

1. Open the **Compress / Resize** tab.
2. Load an image, set format to **jpg**, quality to **80**.
3. Optionally set a max-width (e.g. 1920) and check **Strip metadata**.
4. Click **Compress / Resize**.
5. Output lands in `outputs/compressed/` with a timestamped filename.

### Upscale an image

1. Open the **Upscale** tab.
2. Drop or browse to your image.
3. Set scale to **4**, model to `realesrgan-x4plus`.
4. Click **Run Upscale**.
5. Output is saved to `outputs/upscaled/`.

### Upscale then compress to a target size

1. Open the **Upscale** tab.
2. Load your image. Set scale and model.
3. Expand **Post-processing options**, check **Auto-compress after upscale**, set target size (e.g. **2 MB**).
4. Click **Run Upscale**.
5. The upscaled result is automatically compressed before saving to `outputs/upscaled/`.

### Batch folder mode

The Batch tab UI skeleton is present but the processing logic is not yet implemented. Clicking Run returns a placeholder message. Full batch support is on the roadmap.

---

## Local-First & Security

pixctl is a single-machine tool:

- All processing runs locally via subprocess (ncnn-vulkan) or Python (Pillow, PyTorch).
- No data leaves your machine.
- No user accounts, API keys, or network requests.
- Output files are written to local directories under the project root.
- The Gradio interface is bound to `127.0.0.1` only — it is not exposed to your local network or the internet.

---

## Output Structure

```
outputs/
  upscaled/     ← Upscale tab results
  compressed/   ← Compress / Resize tab results
  batch/        ← Batch tab results (placeholder)
temp/           ← Transient working files (auto-cleaned per run)
```

All output filenames include a timestamp to avoid collisions.

---

## Venv & Dependencies

### Requirements

- Python 3.9+
- `gradio >= 4.0.0`
- `Pillow >= 10.0.0`

Dependencies are installed automatically by `start.sh`. No system-wide packages are installed or modified.

### Recreating the venv

If the venv becomes broken (e.g. after a Python upgrade or corrupted install):

```bash
rm -rf .venv
./start.sh
```

### Manual setup (without start.sh)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## Limitations

- **Batch tab is not yet implemented.** The UI skeleton is present but clicking Run returns a placeholder message.
- **Upscaling requires an external binary or Python script.** Neither is bundled; you must install a backend separately.
- **Face enhancement requires the Python script backend.** The ncnn-vulkan binary does not support it; the option is silently ignored if selected without the correct backend.
- **No progress bar during upscaling.** Long jobs (high resolution, 4× scale) run silently until complete.
- **Single-image processing only** in the Upscale and Compress tabs.
- **JPEG quality reduction is stepped** (decrements of 5 from the chosen quality). Very aggressive target sizes may also trigger progressive downsampling.
- **PNG files are not quality-compressed** — target file size is enforced via downsampling only for PNG output.

---

## Roadmap

- [ ] Full batch folder processing (UI skeleton exists, logic pending)
- [ ] Progress indicator during upscale jobs
- [ ] Drag-and-drop multi-file input
- [ ] Additional Real-ESRGAN model presets

---

## Documentation

- [HOWTO.md](docs/HOWTO.md) — step-by-step usage guide
- [Real-ESRGAN Setup](docs/REAL_ESRGAN_SETUP.md) — how to install and configure a backend
- [Troubleshooting](docs/TROUBLESHOOTING.md) — common problems and fixes

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, code style guidelines, and pull request rules (including the no-large-binaries policy).

---

## Security

pixctl is local-first — no data leaves your machine. For important notes on Gradio network exposure, subprocess trust, and how to report vulnerabilities privately, see [SECURITY.md](SECURITY.md).

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of releases and notable changes.

---

## License

MIT — see [LICENSE](LICENSE).
