# pixctl — Release Readiness Report

**Date:** 2026-05-21  
**Audited by:** RailTaskLite automated audit  
**Scope:** `/home/glitch/Projects/pixctl`

---

## 1. Public Repo Verdict

**CONDITIONAL PASS — Ready to publish after two mandatory pre-push steps.**

The project is structurally complete and clean. All source files compile. No secrets, model files, or large binaries are present. The `.gitignore` correctly excludes all generated, transient, and optional-backend files. Two blockers must be resolved before the first public push: (a) the repository has not yet been initialized with `git init`, and (b) the literal `<repo-url>` placeholder appears in README.md and CONTRIBUTING.md and must be replaced with the actual GitHub URL.

---

## 2. What Is Ready

| Check | Status | Evidence |
|---|---|---|
| `app.py` exists | PASS | File present |
| `requirements.txt` exists | PASS | `gradio>=4.0.0`, `Pillow>=10.0.0` |
| `LICENSE` exists | PASS | MIT, 2026 Cezary Bachlej |
| `README.md` exists and is accurate | PASS | Describes all tabs, limitations, and backend setup accurately |
| `CHANGELOG.md` exists | PASS | v0.1.0 entry dated 2026-05-21 |
| `CONTRIBUTING.md` exists | PASS | Includes no-large-binaries policy |
| `SECURITY.md` exists | PASS | Covers Gradio exposure, subprocess trust, and private reporting |
| `start.sh` exists and is executable | PASS | `-rwxrwxr-x`, shebang `#!/usr/bin/env bash` confirmed |
| Gradio launch command valid | PASS | `demo.launch(server_name=HOST, server_port=PORT)` → `127.0.0.1:7860` |
| All Python source compiles | PASS | `python -m py_compile app.py src/*.py` → exit 0 |
| `.gitignore` covers `.venv/` | PASS | Pattern `.venv/` present |
| `.gitignore` covers `__pycache__/` and `*.pyc` | PASS | Both patterns present |
| `.gitignore` covers `outputs/` | PASS | Pattern present |
| `.gitignore` covers `temp/` | PASS | Pattern present |
| `.gitignore` covers `.env` | PASS | Pattern present |
| `.gitignore` covers model weights | PASS | `*.pth`, `*.bin`, `*.param`, `weights/`, `models/` all present |
| `.gitignore` covers Real-ESRGAN paths | PASS | `Real-ESRGAN/`, `realesrgan-ncnn-vulkan`, `realesrgan-ncnn-vulkan.exe` all present |
| Real-ESRGAN not bundled | PASS | No `Real-ESRGAN/` dir, no binary, no model files anywhere outside `.venv` |
| No `.pth`/`.bin`/`.param` model files | PASS | `find` returned nothing outside `.venv` |
| No files >1 MB (outside `.venv`) | PASS | `find -size +1M` returned nothing |
| `outputs/` directories are empty | PASS | `batch/`, `compressed/`, `upscaled/` all empty |
| `temp/` directory is empty | PASS | Confirmed |
| No API keys or secrets in source | PASS | Grep of `app.py`, `src/`, `start.sh`, `requirements.txt` for common secret patterns returned nothing |
| No `.env` file present | PASS | Not found |
| All README internal doc links resolve | PASS | `docs/HOWTO.md`, `docs/REAL_ESRGAN_SETUP.md`, `docs/TROUBLESHOOTING.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `LICENSE` all exist |
| `docs/screenshots/` directory exists | PASS | Present with `.gitkeep` and placeholder README |
| README accurately notes batch tab is not implemented | PASS | Explicitly stated in Features, Limitations, and Roadmap |
| README accurately notes screenshots not yet included | PASS | Noted in Screenshots section |

---

## 3. What Is Not Ready

| Issue | Severity | Detail |
|---|---|---|
| No git repository initialized | **BLOCKER** | No `.git/` directory exists. `git init` must be run before any commit or push. |
| `<repo-url>` placeholder not filled | **BLOCKER** | `README.md:39` and `CONTRIBUTING.md:10` contain the literal string `<repo-url>`. Must be replaced with the actual GitHub clone URL before publishing. |
| Three internal audit files present | Minor | `PIXELFORGE_PROGRESS_AUDIT.md`, `PROJECT_FINAL_AUDIT.md`, `UI_AUDIT_REPORT.md` are development-phase audit documents. They are not dangerous but add noise to a public repository. Consider removing or archiving them before the first push. |
| No screenshots | Cosmetic | `docs/screenshots/` contains only `.gitkeep` and a placeholder README. The app works without them, but screenshots improve discoverability. |
| Batch tab not implemented | Documented limitation | The batch processing backend is a UI skeleton only. This is clearly documented in README, HOWTO, and the UI itself — no action needed for release, but it is a known gap. |

---

## 4. GitHub Blockers

These must be resolved before the repository can be pushed to GitHub:

1. **`git init` not run.** The project directory has no `.git/`. Without initializing a git repository, no commits can be made and nothing can be pushed.

2. **`<repo-url>` placeholder.** The literal text `<repo-url>` appears in:
   - `README.md` line 39: `` git clone <repo-url> pixctl ``
   - `CONTRIBUTING.md` line 10: `` git clone <repo-url> pixctl ``
   
   Replace both with the actual HTTPS or SSH URL of the GitHub repository (e.g. `https://github.com/your-username/pixctl.git`) before the first public push.

---

## 5. Recommended Git Commands

Run these in order, in `/home/glitch/Projects/pixctl`:

```bash
# Step 1: Initialize the repository
git init

# Step 2: Stage all source files (gitignore will exclude .venv, __pycache__, outputs, temp)
git add app.py requirements.txt README.md LICENSE CHANGELOG.md CONTRIBUTING.md SECURITY.md start.sh .gitignore
git add src/
git add docs/

# Step 3: Optionally add or exclude the audit files (see section 7)
# To include:  git add PIXELFORGE_PROGRESS_AUDIT.md PROJECT_FINAL_AUDIT.md UI_AUDIT_REPORT.md
# To exclude:  add these filenames to .gitignore or leave them unstaged

# Step 4: First commit
git commit -m "chore: initial public release — pixctl v0.1.0"

# Step 5: Add GitHub remote (replace with your actual URL)
git remote add origin https://github.com/your-username/pixctl.git

# Step 6: Push
git push -u origin main
```

**Before step 5:** edit `README.md` line 39 and `CONTRIBUTING.md` line 10 to replace `<repo-url>` with your actual GitHub URL.

---

## 6. Recommended First Release Tag

```
v0.1.0
```

This matches the `[0.1.0] - 2026-05-21` entry already present in `CHANGELOG.md`. After pushing, create the tag:

```bash
git tag -a v0.1.0 -m "pixctl v0.1.0 — initial public release"
git push origin v0.1.0
```

---

## 7. Files That Should Not Be Committed

The following are automatically excluded by `.gitignore` (verified patterns present):

- `.venv/` — Python virtual environment (large, machine-specific)
- `__pycache__/` and `*.pyc` — compiled bytecode (auto-generated; `./__pycache__/` and `./src/__pycache__/` are present locally and will be ignored correctly)
- `outputs/` — user-generated image output directories
- `temp/` — transient working files
- `.env` — environment variable file (currently absent; covered preventively)
- `Real-ESRGAN/`, `realesrgan-ncnn-vulkan`, `realesrgan-ncnn-vulkan.exe` — optional backends not bundled
- `*.pth`, `*.bin`, `*.param`, `weights/`, `models/` — model weight files

The following are **not** excluded by `.gitignore` but should be reviewed before committing:

- `PIXELFORGE_PROGRESS_AUDIT.md` — internal development audit document
- `PROJECT_FINAL_AUDIT.md` — internal development audit document
- `UI_AUDIT_REPORT.md` — internal development audit document
- `RELEASE_READINESS_REPORT.md` — this file (current audit; decide whether to include or exclude)

To exclude these audit files without modifying `.gitignore` permanently, add them to `.gitignore` or simply do not `git add` them.

---

## 8. Final Checklist

- [ ] Run `git init` in `/home/glitch/Projects/pixctl`
- [ ] Replace `<repo-url>` in `README.md` line 39 with actual GitHub URL
- [ ] Replace `<repo-url>` in `CONTRIBUTING.md` line 10 with actual GitHub URL
- [ ] Decide whether to include or exclude the three internal audit files (`PIXELFORGE_PROGRESS_AUDIT.md`, `PROJECT_FINAL_AUDIT.md`, `UI_AUDIT_REPORT.md`)
- [ ] Create the GitHub repository (public)
- [ ] Run `git add` for source files (use staged adds, not `git add .`, to avoid accidentally including any future-generated files)
- [ ] Verify `git status` shows no unexpected files staged
- [ ] Commit and push
- [ ] Create and push tag `v0.1.0`
- [ ] Confirm GitHub repository page renders README correctly
- [ ] (Optional) Add screenshots to `docs/screenshots/` in a follow-up commit

---

## Commands Run During This Audit

```bash
ls -la /home/glitch/Projects/pixctl/
find /home/glitch/Projects/pixctl -maxdepth 3 -type f | sort
cat /home/glitch/Projects/pixctl/.gitignore
cat /home/glitch/Projects/pixctl/README.md
cat /home/glitch/Projects/pixctl/app.py
cat /home/glitch/Projects/pixctl/start.sh
cat /home/glitch/Projects/pixctl/requirements.txt
cat /home/glitch/Projects/pixctl/src/config.py
cat /home/glitch/Projects/pixctl/src/ui.py
cat /home/glitch/Projects/pixctl/src/realesrgan_runner.py
cat /home/glitch/Projects/pixctl/src/image_ops.py
cat /home/glitch/Projects/pixctl/src/utils.py
cat /home/glitch/Projects/pixctl/docs/HOWTO.md
cat /home/glitch/Projects/pixctl/docs/REAL_ESRGAN_SETUP.md
cat /home/glitch/Projects/pixctl/docs/TROUBLESHOOTING.md
cat /home/glitch/Projects/pixctl/SECURITY.md
cat /home/glitch/Projects/pixctl/CONTRIBUTING.md
cat /home/glitch/Projects/pixctl/LICENSE
cat /home/glitch/Projects/pixctl/CHANGELOG.md
cat /home/glitch/Projects/pixctl/docs/screenshots/README.md
ls /home/glitch/Projects/pixctl/.git  # → no git repo
find … -name "*.pth" -o -name "*.bin" -o -name "*.param" -o -name "*.onnx" -o -name "*.pt"  # → nothing
grep -rn … (secret/API key patterns) app.py src/ start.sh requirements.txt  # → nothing
ls -la outputs/batch outputs/compressed outputs/upscaled temp/  # → all empty
find … -maxdepth 2 -size +1M  # → nothing
find … -name "Real-ESRGAN" -type d / -name "realesrgan*"  # → nothing outside .venv
grep -n links README.md; verify each path exists  # → all OK
cd /home/glitch/Projects/pixctl && python -m py_compile app.py src/*.py  # → exit 0
```

## Files Inspected

- `app.py`, `src/config.py`, `src/ui.py`, `src/image_ops.py`, `src/realesrgan_runner.py`, `src/utils.py`, `src/__init__.py`
- `start.sh`, `requirements.txt`, `.gitignore`
- `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`
- `docs/HOWTO.md`, `docs/REAL_ESRGAN_SETUP.md`, `docs/TROUBLESHOOTING.md`, `docs/screenshots/README.md`

---

## Exact Next Command for the User

```bash
cd /home/glitch/Projects/pixctl && git init
```

Then edit `README.md:39` and `CONTRIBUTING.md:10` to replace `<repo-url>` with your GitHub URL, and proceed with the staged `git add` commands in Section 5.
