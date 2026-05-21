# pixctl — HOWTO

Step-by-step usage guide for pixctl.

---

## First Run

1. Clone the repository and enter the project directory.
2. Run `./start.sh`:

   ```bash
   ./start.sh
   ```

   On first run this creates a `.venv/` virtual environment in the project root and installs `gradio` and `Pillow` into it. Depending on your download speed this takes 20–60 seconds.

3. Once the install completes, the app starts and prints a URL:

   ```
   Running on local URL:  http://127.0.0.1:7860
   ```

4. Open that URL in your browser. If Gradio detects a browser it may open it automatically; otherwise paste the URL manually.

---

## Normal Run (after first run)

```bash
./start.sh
```

The venv already exists, so `pip install` reports "Requirement already satisfied" and exits quickly. The app starts in a few seconds.

---

## Compress-Only Workflow

1. Open the **Compress / Resize** tab.
2. Click **Browse** or drag an image onto the input area.
3. Select the output **Format** (JPEG, PNG, WebP).
4. For JPEG or WebP, set a **Quality** value (1–100; higher = better quality, larger file).
5. Optionally set a **Max width** to downsample large images (choices: 1280, 1920, 2560, 3840 px, or Original).
6. Optionally set a **Target file size** (1 MB, 2 MB, 5 MB, 10 MB). The app reduces quality iteratively to meet the target. If it cannot, it warns and saves at the smallest achievable size.
7. Optionally check **Strip metadata** to remove EXIF and other embedded data.
8. Click **Compress / Resize**.
9. The output path and size stats appear in the results panel.

---

## Upscale Workflow

Before using this workflow, a Real-ESRGAN backend must be installed and detected. See [REAL_ESRGAN_SETUP.md](REAL_ESRGAN_SETUP.md).

1. Open the **Upscale** tab.
2. Check the backend status badge in the header. If it reads **No backend**, the Run button will be disabled — install a backend and restart.
3. Click **Browse** or drag an image onto the input area.
4. Select **Scale** (2× or 4×).
5. Select a **Model**:
   - `realesrgan-x4plus` — general photos
   - `realesrgan-x4plus-anime` — anime/illustration
   - `realesr-animevideov3` — anime video frames
6. Optionally check **Face enhancement** (only active with the Python script backend).
7. Optionally expand **Post-processing options** and enable **Auto-compress after upscale** with a quality, max-width, or target size.
8. Click **Run Upscale**.
9. The result is saved to `outputs/upscaled/` and the path is shown in the results panel.

---

## Batch Workflow

The Batch Folder Mode tab is a UI skeleton. The underlying processing logic is not yet implemented. Clicking Run returns a placeholder message.

Full batch support is planned — see the Roadmap in [README.md](../README.md).

---

## Where Output Files Are Saved

All outputs are saved under the project root:

| Tab | Output directory |
|-----|-----------------|
| Upscale | `outputs/upscaled/` |
| Compress / Resize | `outputs/compressed/` |
| Batch | `outputs/batch/` (placeholder) |

Filenames include a timestamp to avoid overwriting previous results. Temporary working files are written to `temp/` and cleaned up automatically each run.

---

## How to Stop the App

Press **Ctrl+C** in the terminal where `./start.sh` is running. The Gradio server shuts down cleanly.

---

## How to Update Dependencies

`start.sh` runs `pip install -r requirements.txt` on every launch, so it picks up new pinned versions automatically when `requirements.txt` is updated.

To force a clean reinstall (e.g. after upgrading Python or if packages are broken):

```bash
rm -rf .venv
./start.sh
```

To manually upgrade a specific package inside the venv:

```bash
source .venv/bin/activate
pip install --upgrade gradio
```
