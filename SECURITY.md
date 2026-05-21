# Security Policy

## Local-first design

pixctl is a single-machine tool. It does **not**:

- Upload images or any data to any remote server
- Make outbound network requests of any kind
- Require user accounts, API keys, or authentication
- Store credentials or personal data

All image processing runs locally via subprocess (ncnn-vulkan binary) or Python (Pillow / PyTorch). Output files are written to local directories under the project root.

---

## Gradio network exposure warning

By default, the Gradio interface is bound to `127.0.0.1` only (localhost). It is **not** exposed to your local network or the internet.

**Do not expose pixctl to a public network or a shared LAN without understanding the implications.** Gradio does not include authentication by default. Anyone who can reach the port can use the UI and trigger subprocesses on your machine. If you need remote access, place a properly configured reverse proxy with authentication in front of it, and do so only if you understand the risks.

---

## Subprocess execution

The Upscale tab invokes an external binary (`realesrgan-ncnn-vulkan`) or a Python script via subprocess. pixctl does not validate or sandbox those executables — it trusts the binary at the configured path. Only point pixctl at executables you obtained from a trusted source and verified yourself.

---

## Reporting a security issue

If you discover a security vulnerability in pixctl, please report it **privately** rather than opening a public issue.

Send a description of the issue, reproduction steps, and potential impact to the repository owner via the contact method listed on the GitHub profile. Please allow reasonable time for a response before any public disclosure.

Do not include sensitive data (your images, file paths, or system details beyond what is necessary to reproduce the issue) in the report.
