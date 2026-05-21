# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

- Full batch folder processing (UI skeleton present, logic pending)
- Progress indicator during upscale jobs
- Drag-and-drop multi-file input

---

## [0.1.0] - 2026-05-21

### Added

- Local Gradio web UI bound to `127.0.0.1:7860` — no accounts, no cloud
- **Compress / Resize tab**: format conversion (JPEG, PNG, WebP), quality slider, max-width downsampling presets, target file size enforcement, EXIF/metadata stripping
- **Real-ESRGAN backend detection**: automatic discovery of ncnn-vulkan binary (PATH, local, nested) and Python script backend, with face-enhancement support when the Python backend is present
- **Upscale tab**: 2× and 4× AI upscaling via detected Real-ESRGAN backend, optional post-upscale auto-compress pass
- **Batch Folder Mode tab**: UI skeleton present for future batch processing
- `start.sh` bootstrap: creates `.venv`, installs `requirements.txt`, launches the app
- Output directories: `outputs/upscaled/`, `outputs/compressed/`, `outputs/batch/`
- Public repository polish: LICENSE (MIT), CHANGELOG, CONTRIBUTING, SECURITY, `.gitignore`
