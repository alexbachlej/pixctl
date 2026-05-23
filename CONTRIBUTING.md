# Contributing to pixctl

Thanks for your interest in contributing. pixctl is a local-first image processing tool — contributions that keep it simple, dependency-light, and offline-capable are most welcome.

---

## Local setup

```bash
git clone <repo-url> pixctl
cd pixctl
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Or use `./start.sh`, which handles venv creation and launch automatically.

**Python version:** 3.9 or newer.

---

## Code style

- Follow PEP 8. Use 4-space indentation.
- Keep functions focused and short. Avoid deep nesting.
- No type annotations are required, but they are welcome for new public functions.
- No linter is enforced yet; just keep diffs readable.

---

## Pull request guidelines

- **No large binaries or model files in PRs.** Do not commit `.pth`, `.param`, `.bin`, ncnn-vulkan executables, or any file over ~1 MB unless there is a compelling reason and explicit discussion first.
- **No new cloud/network dependencies.** pixctl must remain fully functional without any internet access at runtime.
- **Keep the scope small.** Fix one thing per PR. If you want to refactor broadly, open an issue to discuss first.
- **Test your changes manually** before submitting. Run the UI and exercise the affected tab.
- **Describe what and why** in your PR description, not just what the diff changes.

---

## Reporting bugs

Open a GitHub issue with:

1. What you did
2. What you expected
3. What actually happened
4. Python version, OS, and which Real-ESRGAN backend (if relevant)

---

## License

By contributing you agree that your contributions will be licensed under the MIT License that covers this project. See [LICENSE](LICENSE).
