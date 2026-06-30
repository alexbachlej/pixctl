# pixctl

[![CI](https://github.com/alexbachlej/pixctl/actions/workflows/ci.yml/badge.svg)](https://github.com/alexbachlej/pixctl/actions/workflows/ci.yml)

<!-- RAILTASKLITE_PROOF_ARTIFACT_START -->
> **RailTaskLite proof artifact**
>
> pixctl is a practical local image optimization and upscaling tool. It is also an inspectable output artifact produced through **RailTaskLite**, my controlled AI execution workflow.
>
> The point of this repository is not only the tool itself. The code is public so you can inspect the quality of software that a constrained AI execution system can produce when work is broken into scoped batches, reviewed through audit gates, repaired through feedback loops, and packaged into a usable project.
>
> **pixctl is the output. RailTaskLite is the execution system behind it.**
<!-- RAILTASKLITE_PROOF_ARTIFACT_END -->

## Why this repository exists

pixctl can be evaluated as a normal software project: it has source code, tests, packaging, documentation, and a usable interface.

But its stronger role is as a proof artifact for RailTaskLite. It demonstrates that the workflow can turn a product goal into working software through controlled AI execution rather than unbounded prompt-and-pray coding.

The important claim is repeatability: scoped tasks, allowed files, audit batches, stop gates, operator decisions, and visible artifacts.

CLI image optimization and upscaling toolkit with Real-ESRGAN support. No accounts, no cloud, no telemetry.

Gradio web UI for upscaling, compression, format conversion, and metadata stripping, powered by [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN). Runs entirely on your machine.

> **Real-ESRGAN is not bundled.** You must install an external backend (ncnn-vulkan binary or Python script) and point pixctl at it. See [docs/REAL_ESRGAN_SETUP.md](docs/REAL_ESRGAN_SETUP.md).

---

## Demo

[![pixctl — upscale comparison](assets/screenshots/Screenshot%20from%202026-05-23%2021-33-57.webp)](https://youtu.be/I6z3NQbGmj8)

[Watch on YouTube →](https://youtu.be/I6z3NQbGmj8)

---

## Screenshots

![pixctl UI — upscale tab with before/after and output stats](assets/screenshots/Screenshot%20from%202026-05-22%2015-46-05.webp)

<table>
<tr>
<td><img src="assets/screenshots/demo5.webp" alt="Pixel-level detail recovery at 4×"></td>
<td><img src="assets/screenshots/Screenshot%20from%202026-05-23%2021-33-57.webp" alt="Before/after — alternate subject"></td>
</tr>
</table>

---

## Features

**Upscale** *(requires Real-ESRGAN backend)*
- 2× and 4× AI upscaling
- Models: `realesrgan-x4plus`, `realesrgan-x4plus-anime`, `realesr-animevideov3`
- Output formats: PNG, JPEG, WebP
- Optional face enhancement (Python script backend only)
- Optional auto-compress pass after upscaling

**Compress / Resize** *(no backend required)*
- Format conversion: JPEG, PNG, WebP
- Quality slider (1–100)
- Max-width presets: 1280, 1920, 2560, 3840 px
- Target file size presets: 1 MB, 2 MB, 5 MB, 10 MB
- EXIF and metadata stripping

---

## Requirements

**pixctl itself**
- Python 3.9+
- `gradio >= 4.0` and `Pillow >= 10.0` — installed automatically by `start.sh`

**Upscale tab** *(requires one of the following, installed separately)*
- `realesrgan-ncnn-vulkan` binary — fastest, no extra Python deps, no face enhancement
- Real-ESRGAN Python project (`inference_realesrgan.py`) — supports face enhancement via GFPGAN

The **Compress / Resize tab** works without any backend.

See [docs/REAL_ESRGAN_SETUP.md](docs/REAL_ESRGAN_SETUP.md) for backend installation.

---

## Quick Start

```bash
git clone https://github.com/alexbachlej/pixctl pixctl
cd pixctl
./start.sh
```

Opens at **http://127.0.0.1:7860** (auto-increments port if busy).

`start.sh` creates `.venv` on first run, installs dependencies only when `requirements.txt` changes, and launches the app. Manual setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## Real-ESRGAN Backend

pixctl auto-detects a backend at startup in this order:

| Priority | Location | Kind |
|----------|-----------|------|
| 0 | `$REAL_ESRGAN_PATH` env var | auto-detected |
| 1 | `realesrgan-ncnn-vulkan` in `$PATH` | ncnn-vulkan binary |
| 2 | `./realesrgan-ncnn-vulkan` | ncnn-vulkan binary |
| 3 | `./Real-ESRGAN/realesrgan-ncnn-vulkan` | ncnn-vulkan binary |
| 4 | `./Real-ESRGAN/inference_realesrgan.py` | Python script |

If no backend is found the Upscale tab loads but Run is disabled. The path can also be set directly in the UI.

Full setup instructions: [docs/REAL_ESRGAN_SETUP.md](docs/REAL_ESRGAN_SETUP.md)

---

## Configuration

| Variable | Effect |
|---|---|
| `PIXCTL_PORT=7865` | Start on a specific port |
| `PIXCTL_OPEN_BROWSER=0` | Disable auto browser-open |
| `PIXCTL_DEBUG=1` | Print backend detection, subprocess args, stdout/stderr |

---

## Output Structure

```
outputs/
  upscaled/     ← Upscale tab results
  compressed/   ← Compress / Resize tab results
  batch/        ← Batch tab results (placeholder)
temp/           ← Transient working files (cleared on startup)
```

---

## Docs

- [docs/HOWTO.md](docs/HOWTO.md) — step-by-step usage guide
- [docs/REAL_ESRGAN_SETUP.md](docs/REAL_ESRGAN_SETUP.md) — backend installation
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) — common problems and fixes
- [CHANGELOG.md](CHANGELOG.md) — release history
- [CONTRIBUTING.md](CONTRIBUTING.md) — local setup and PR rules
- [SECURITY.md](SECURITY.md) — vulnerability reporting and Gradio network notes

---

## License

MIT — see [LICENSE](LICENSE).

---

## Roadmap

- **Batch Folder Mode** — process an entire folder in one pass (UI tab exists; processing pipeline in progress)

---

<sub>Development orchestrated with RailTaskLite.</sub>
