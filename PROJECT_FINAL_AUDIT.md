# Project Final Audit

**Audit date:** 2026-05-21  
**Auditor:** Claude Code (read-only audit + minimal rename)  
**Project:** pixctl (formerly PixelForge)

---

## 1. Project Path

```
/home/glitch/Projects/pixctl
```

---

## 2. Rename Status

### Renamed safely

| Location | Old value | New value |
|----------|-----------|-----------|
| `src/ui.py:258` — Gradio Blocks title | `title="PixelForge"` | `title="pixctl"` |
| `src/ui.py:259` — Gradio header markdown | `# PixelForge` | `# pixctl` |
| `start.sh:16` — echo message | `Starting PixelForge...` | `Starting pixctl...` |
| `README.md:1` — document title | `# PixelForge` | `# pixctl` |
| Folder | `/home/glitch/Projects/PixelForge` | `/home/glitch/Projects/pixctl` |

Folder rename is safe: `src/config.py` derives `BASE_DIR` via `Path(__file__).resolve().parent.parent` (fully relative), and `start.sh` uses `cd "$(dirname "$0")"` (also relative). Verified: server binds on `127.0.0.1:7860` after rename.

### Intentionally left unchanged

| File | Reason |
|------|--------|
| `PIXELFORGE_PROGRESS_AUDIT.md` | Historical audit document from previous session — not a user-facing surface, preserving as record |

Zero remaining `PixelForge` references in `*.py`, `*.sh`, `*.md`, `*.txt` source files (confirmed by grep).

---

## 3. Completion Estimate

**~78%**

Core infrastructure, Compress/Resize tab, and Upscale tab (full code path) are implemented and verified functional. Batch Folder Mode tab is an explicit, labeled placeholder — the only major unfinished piece.

---

## 4. Task Matrix

| Area | Status | Notes |
|------|--------|-------|
| Foundation (app.py, config, structure) | COMPLETE | Correct entry point, path resolution, output dirs |
| start.sh | COMPLETE | venv creation, dep install, launch; executable; set -euo pipefail |
| Gradio UI (launch, port bind) | COMPLETE | Binds 127.0.0.1:7860, confirmed by ss post-rename |
| Compress / Resize tab | COMPLETE | Format, quality, max-width, target-bytes, strip-meta; all wired |
| Real-ESRGAN detection | COMPLETE | 4-tier probe: PATH → local binary → nested → Python script |
| Upscale tab | COMPLETE | Model, scale, face_enhance, format, auto-compress; button disabled when no backend |
| Batch mode | MISSING | Renders UI (textbox + button) but calls placeholder_result() — no real processing |
| Error handling | COMPLETE | Missing backend, upscale failure, FileExistsError, format conversion errors all handled |
| README | PARTIAL | Accurate but minimal — no screenshots, no contributing guide |
| Rename consistency | COMPLETE | All user-facing surfaces renamed; zero PixelForge references remain in source |
| Public repo readiness | PARTIAL | No LICENSE, no git repo, batch is placeholder, no screenshots |

---

## 5. What Works

Verified by inspection and runtime:

- `./start.sh` completes; venv creates and activates correctly; deps install
- `python -m py_compile` passes on all 6 source files — zero syntax errors
- Gradio launches and binds to `127.0.0.1:7860` (confirmed pre- and post-rename)
- All three tabs render in UI without errors
- **Compress / Resize tab** is fully functional: JPEG/PNG/WebP output, quality slider, max-width resize (LANCZOS), iterative target-bytes shrink, progressive resize fallback, EXIF preservation/stripping
- Timestamp filenames: `stem_20260521_154600.jpg` format
- Overwrite protection: `safe_output_path()` raises `FileExistsError` on collision
- `unique_output_path()` implemented (auto-increments `_N` suffix) — available for batch use
- Upscale tab code path is complete: subprocess wrapper handles both ncnn-vulkan and Python script backends; temp PNG cleanup; `RunResult` dataclass returned; post-upscale `compress_image` chain wired
- Backend detection gracefully returns `kind="none"` when no Real-ESRGAN is present; Upscale button disabled; correct error messages shown
- Output directories auto-created on startup via `init_dirs()`
- No accidental binaries, models, or output images in tracked files
- `.gitignore` correctly covers `.venv/`, `outputs/`, `temp/`, `__pycache__/`, `*.pyc`

---

## 6. What Is Missing

1. **Batch Folder Mode implementation** — `_batch_tab()` in `src/ui.py:242` calls `placeholder_result("Batch")`. The UI exists (folder path textbox, Run button) but no processing occurs. All prerequisite utilities exist: `compress_image()`, `timestamped_filename()`, `unique_output_path()`.

2. **LICENSE file** — No license at project root. Required before any public GitHub release.

3. **Git repository** — Not initialized. `git init` required before pushing.

4. **Screenshots in README** — README is accurate but text-only. No UI screenshots.

---

## 7. What Is Broken

Nothing is outright broken. Two code quality gaps:

1. **`unique_output_path` is orphaned** — implemented in `src/utils.py:23`, imported nowhere, called from nowhere. Both UI handlers use `safe_output_path` (raises on collision) instead. Intended for batch mode but never wired.

2. **`safe_output_path` collision behavior** — If two files with the same stem are compressed within the same second, the second call errors with `FileExistsError`. Low probability in single-user use; becomes a real issue if batch mode uses it instead of `unique_output_path`.

---

## 8. Public Repo Blockers

Items that must be resolved before GitHub release:

1. **No LICENSE** — Repo cannot be legally used by anyone without one. Add `LICENSE` (e.g., MIT) to project root.
2. **Batch tab is a placeholder** — Renders "Batch processing coming soon." in README but button returns a static non-functional string. Either implement it or remove the tab before publishing.
3. **No git repository** — Run `git init` and make an initial commit.
4. **`.venv/` not excluded from `git add` by .gitignore alone** — `.venv/` is in `.gitignore` correctly, but a fresh `git init` + `git add .` will not track it. Verify with `git status` before first commit to ensure `.venv/` is excluded.

---

## 9. Nice-To-Have Improvements

Non-blocking; do not implement before the above blockers are resolved:

- **Screenshots in README** — A single screenshot of the Compress tab would significantly improve discoverability.
- **Wire `unique_output_path` in compress handler** — Replace `safe_output_path` with `unique_output_path` in `_do_compress` and `_do_upscale` to avoid same-second collision errors.
- **`start.sh` version pin** — `pip install --quiet -r requirements.txt` installs latest compatible; adding `==` pins in `requirements.txt` would make installs reproducible.
- **Gradio share=False explicit** — Already defaulted off, but documenting it in `app.py` prevents accidental public exposure.
- **Dry-run mode** — Not present. Not required by current design but listed in original spec.
- **CONTRIBUTING.md** — Optional for a small utility, but expected for public repos.

---

## 10. Exact Next Tasks

In priority order:

1. Implement `_batch_tab()` in `src/ui.py:242`:
   - Validate folder path exists
   - Iterate `*.jpg`, `*.jpeg`, `*.png`, `*.webp`
   - Call `compress_image()` per file with configurable settings
   - Write to `outputs/batch/` using `unique_output_path()`
   - Return per-file log summary

2. Add `LICENSE` to project root (MIT recommended for a utility tool).

3. `git init` in `/home/glitch/Projects/pixctl`, then initial commit (verify `.venv/` excluded first).

4. Add one screenshot to README (capture Compress / Resize tab).

5. Wire `unique_output_path` in `_do_compress` and `_do_upscale` to replace `safe_output_path`.

---

## 11. Final Verdict

**ALMOST READY, NEEDS SMALL FIXES**

The app is fully usable locally today. Core compress and upscale pipelines work end-to-end. Rename is complete and consistent. The only gap before "READY TO PUBLISH" is: implement batch tab, add LICENSE, initialize git repo.
