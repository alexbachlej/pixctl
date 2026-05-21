# Troubleshooting

Common problems and fixes for pixctl.

---

## Port Already in Use

**Symptom:** The app fails to start with an error like `OSError: [Errno 98] Address already in use` or `Address '127.0.0.1:7860' is already in use`.

**Fix:** Another process (a previous pixctl instance or another Gradio app) is occupying port 7860. Find and stop it:

```bash
# Find the process using port 7860
lsof -i :7860
# or
ss -tlnp | grep 7860

# Stop it by PID
kill <PID>
```

Then re-run `./start.sh`.

Alternatively, change the port by editing `PORT` in `src/config.py`:

```python
PORT = 7861   # or any free port
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
2. Check that the binary or script is at one of the four detected paths (in order):
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

**Fix:** Open the URL manually. The terminal prints:

```
Running on local URL:  http://127.0.0.1:7860
```

Copy and paste that URL into your browser.

---

## Gradio Launches but UI Is Unavailable

**Symptom:** The terminal shows the Gradio URL and no errors, but opening the URL in the browser shows a blank page, a connection refused error, or an endless loading spinner.

**Possible causes:**

- **Wrong URL:** The app binds to `127.0.0.1:7860`. Make sure you are accessing it from the same machine. It is not accessible from other machines on the network by design.
- **Firewall or proxy:** A local firewall rule or browser proxy may be blocking `127.0.0.1`. Disable the proxy for local addresses.
- **Gradio still starting up:** Gradio can take a second or two to be ready after printing the URL. Wait a moment and refresh.
- **Port conflict:** Another process grabbed 7860 between app start and the browser request. Check with `lsof -i :7860` and see the [Port Already in Use](#port-already-in-use) section.
- **Crash after startup:** Scroll the terminal for a Python traceback. If the app crashed immediately after printing the URL, restart with `./start.sh` and read the full output.
