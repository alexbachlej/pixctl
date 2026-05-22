import threading
import time
from pathlib import Path

import gradio as gr
from PIL import Image as PILImage

from src.config import OUTPUTS, TEMP_DIR, load_local_config, save_local_config
from src.image_ops import MAX_WIDTHS, TARGET_SIZES, compress_image
from src.realesrgan_runner import detect_backend, run_upscale
from src.utils import placeholder_result, safe_output_path, timestamped_filename

_UPSCALE_MODELS = [
    "realesrgan-x4plus",
    "realesrgan-x4plus-anime",
    "realesr-animevideov3",
]

THEME = gr.themes.Ocean()

CUSTOM_CSS = """
/* ── pixctl · creator-tool theme ── */

/* Typography */
body, .gradio-container {
    font-family: 'Inter', 'SF Pro Display', ui-sans-serif, system-ui, -apple-system, sans-serif !important;
}
textarea {
    font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace !important;
    font-size: 11.5px !important;
    line-height: 1.65 !important;
}
input[type="range"] {
    accent-color: #818cf8 !important;
}

/* Tab navigation */
.tab-nav {
    border-bottom: 1px solid rgba(255, 255, 255, 0.07) !important;
    margin-bottom: 12px !important;
}
.tab-nav button {
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    border-radius: 6px 6px 0 0 !important;
    transition: color 0.15s, background 0.15s !important;
}

/* ── Header ── */
.pixctl-header {
    background: linear-gradient(135deg, #0d1117 0%, #101722 65%, #0c181a 100%);
    border: 1px solid rgba(34, 211, 238, 0.18);
    border-radius: 10px;
    padding: 18px 22px 15px;
    margin-bottom: 6px;
    box-shadow:
        0 4px 20px rgba(0, 0, 0, 0.50),
        inset 0 1px 0 rgba(34, 211, 238, 0.10);
}
.pixctl-header h1 {
    margin: 0 0 4px;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: #e8edf8;
    line-height: 1.2;
}
.pixctl-header .tagline {
    font-size: 12px;
    color: #8496b8;
    margin-bottom: 10px;
    letter-spacing: 0.1px;
}

/* ── Backend badge ── */
.backend-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.backend-ok {
    background: rgba(34, 197, 94, 0.08);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.18);
}
.backend-none {
    background: rgba(148, 163, 184, 0.07);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.18);
}

/* ── Workflow hint strip ── */
.workflow-hint {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 2px 10px;
    flex-wrap: wrap;
}
.wf-step {
    padding: 2px 9px;
    border-radius: 4px;
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 0.2px;
    color: #818cf8;
    background: rgba(129, 140, 248, 0.08);
    border: 1px solid rgba(129, 140, 248, 0.15);
}
.wf-arrow {
    font-size: 11px;
    color: rgba(129, 140, 248, 0.35);
}

/* ── Backend unavailable notice ── */
.backend-unavailable-notice {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 16px;
    border-radius: 8px;
    background: rgba(148, 163, 184, 0.04);
    border: 1px solid rgba(148, 163, 184, 0.13);
    margin-bottom: 10px;
}
.bun-icon {
    font-size: 15px;
    line-height: 1.45;
    flex-shrink: 0;
    color: #64748b;
}
.bun-body {
    font-size: 12.5px;
    line-height: 1.6;
}
.bun-title {
    display: block;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 3px;
}
.bun-detail {
    display: block;
    color: rgba(148, 163, 184, 0.55);
    font-size: 11px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

/* ── Disabled action button — intentional, not broken ── */
button[disabled] {
    opacity: 0.38 !important;
    cursor: not-allowed !important;
    filter: none !important;
    background: rgba(148, 163, 184, 0.08) !important;
    border-color: rgba(148, 163, 184, 0.18) !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
}

/* ── Batch placeholder ── */
.batch-coming-soon {
    font-size: 12px;
    color: #56637a;
    padding: 2px 2px 12px;
}

/* ── Info card ── */
.info-card {
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px 20px;
    margin-top: 4px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    background: rgba(0, 0, 0, 0.18);
}
.info-metric {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 72px;
}
.info-metric-label {
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    opacity: 0.45;
}
.info-metric-value {
    font-size: 13px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}
.info-metric-value.dim { opacity: 0.3; }
.info-metric-value.good { color: #4ade80; }

/* ── Upscale active-processing strip ── */
.upscale-progress {
    position: relative;
    overflow: hidden;
    border-radius: 22px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 600;
    color: #e2f7ff;
    background: linear-gradient(90deg, #1e3a8a 0%, #0e7490 55%, #065f46 100%);
    letter-spacing: 0.25px;
    margin: 4px 0;
    box-shadow: 0 2px 14px rgba(6, 182, 212, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.07);
    user-select: none;
}
.upscale-progress::after {
    content: '';
    position: absolute;
    top: 0;
    left: -60%;
    width: 60%;
    height: 100%;
    background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.18) 50%, transparent 100%);
    animation: upscale-shimmer 1.8s ease-in-out infinite;
    pointer-events: none;
}
@keyframes upscale-shimmer {
    0%   { left: -60%; }
    100% { left: 120%; }
}
.upscale-done {
    border-radius: 22px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 600;
    color: #4ade80;
    background: rgba(34, 197, 94, 0.08);
    border: 1px solid rgba(34, 197, 94, 0.20);
    margin: 4px 0;
    letter-spacing: 0.1px;
}
.upscale-fail {
    border-radius: 22px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 600;
    color: #f87171;
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.20);
    margin: 4px 0;
    letter-spacing: 0.1px;
}
"""


# ── Info card helpers ──────────────────────────────────────────────────────────

def _info_card_html(metrics: list[tuple[str, str, str]]) -> str:
    items = "".join(
        f'<div class="info-metric">'
        f'<div class="info-metric-label">{lbl}</div>'
        f'<div class="info-metric-value {cls}">{val}</div>'
        f'</div>'
        for lbl, val, cls in metrics
    )
    return f'<div class="info-card">{items}</div>'


def _empty_input_info() -> str:
    return _info_card_html([
        ("Dimensions", "—", "dim"),
        ("File size", "—", "dim"),
    ])


def _empty_output_info() -> str:
    return _info_card_html([
        ("Output size", "—", "dim"),
        ("Ratio", "—", "dim"),
        ("Format", "—", "dim"),
    ])


def _status_processing(text: str) -> str:
    return f'<div class="upscale-progress">{text}</div>'


def _status_done(text: str) -> str:
    return f'<div class="upscale-done">{text}</div>'


def _status_fail(text: str) -> str:
    return f'<div class="upscale-fail">{text}</div>'


def _input_image_info(img_path: str | None) -> str:
    if not img_path:
        return _empty_input_info()
    try:
        path = Path(img_path)
        size_kb = path.stat().st_size / 1024
        with PILImage.open(path) as im:
            w, h = im.size
        return _info_card_html([
            ("Dimensions", f"{w} × {h} px", ""),
            ("File size", f"{size_kb:.1f} KB", ""),
        ])
    except Exception:
        return _empty_input_info()


def _build_header_html() -> str:
    return (
        '<div class="pixctl-header">'
        '<h1>pixctl</h1>'
        '<div class="tagline">Local image processing toolkit · AI upscale · compress · resize</div>'
        '</div>'
    )


# ── Upscale tab ───────────────────────────────────────────────────────────────

def _do_upscale(
    user_backend_path: str,
    img_path: str | None,
    scale_str: str,
    model: str,
    face_enhance: bool,
    fmt: str,
    quality: int,
    auto_compress: bool,
    max_width_str: str,
    target_size_str: str,
):
    """Generator — yields (img_out, log, out_info, btn_update, status) for live UI feedback."""

    _BTN_IDLE = gr.update(interactive=True, value="Run Upscale")

    # Immediately disable button and clear stale output
    yield None, "Starting...", _empty_output_info(), gr.update(interactive=False, value="Running..."), _status_processing("Starting upscale…")

    backend = detect_backend(user_backend_path or None)

    if not img_path:
        yield None, "No input image provided.", _empty_output_info(), _BTN_IDLE, _status_fail("No input image")
        return
    if not backend.available:
        yield (
            None,
            "Real-ESRGAN backend is required. Add a valid Real-ESRGAN folder or executable path.\n"
            "Examples: /path/to/Real-ESRGAN  or  /path/to/realesrgan-ncnn-vulkan\n"
            "Compression is still available without it.",
            _empty_output_info(),
            _BTN_IDLE,
            _status_fail("No backend available"),
        )
        return

    # Run the blocking subprocess in a background thread so the UI stays live
    result_bag: list = [None, None]  # [result_tuple, exception]

    def _worker() -> None:
        try:
            input_path = Path(img_path)
            scale = int(scale_str)
            input_size = input_path.stat().st_size

            tmp_name = timestamped_filename(f"{input_path.stem}_x{scale}_raw", ".png")
            tmp_path = TEMP_DIR / tmp_name

            run_result = run_upscale(
                backend,
                input_path,
                tmp_path,
                model=model,
                scale=scale,
                face_enhance=face_enhance,
            )

            if not run_result.success:
                lines = [f"Upscale failed (exit {run_result.returncode}, {run_result.duration:.1f}s)"]
                if run_result.stderr:
                    lines.append(f"stderr: {run_result.stderr.strip()}")
                if run_result.stdout:
                    lines.append(f"stdout: {run_result.stdout.strip()}")
                result_bag[0] = (None, "\n".join(lines), _empty_output_info())
                return

            out_name = timestamped_filename(f"{input_path.stem}_x{scale}", f".{fmt}")
            try:
                output_path = safe_output_path(OUTPUTS["upscaled"], out_name)
            except FileExistsError as exc:
                if tmp_path.exists():
                    tmp_path.unlink()
                result_bag[0] = (None, str(exc), _empty_output_info())
                return

            target_bytes = TARGET_SIZES.get(target_size_str) if auto_compress else None
            max_width = MAX_WIDTHS.get(max_width_str) if auto_compress else None

            try:
                compress_result = compress_image(
                    input_path=tmp_path,
                    output_path=output_path,
                    fmt=fmt,
                    quality=quality,
                    max_width=max_width,
                    target_bytes=target_bytes,
                    strip_metadata=False,
                )
            except Exception as exc:
                result_bag[0] = (None, f"Post-process error: {exc}", _empty_output_info())
                return
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()

            if user_backend_path:
                save_local_config({"realesrgan_path": user_backend_path})

            in_kb = input_size / 1024
            out_kb = compress_result["output_size"] / 1024
            ratio = out_kb / in_kb if in_kb > 0 else 1.0
            log = (
                f"Elapsed: {run_result.duration:.0f}s\n"
                f"Saved:  {compress_result['output_path']}\n"
                f"Before: {in_kb:.1f} KB  →  After: {out_kb:.1f} KB\n"
                f"{compress_result['log']}"
            )
            ratio_cls = "good" if ratio < 1.0 else ""
            info_html = _info_card_html([
                ("Output size", f"{out_kb:.1f} KB", ""),
                ("vs input", f"{ratio * 100:.0f}%", ratio_cls),
                ("Scale", f"×{scale}", ""),
                ("Format", fmt.upper(), "dim"),
                ("Duration", f"{run_result.duration:.1f}s", "dim"),
            ])
            result_bag[0] = (str(compress_result["output_path"]), log, info_html)
        except Exception as exc:
            result_bag[1] = exc

    thread = threading.Thread(target=_worker, daemon=True)
    t0 = time.monotonic()
    thread.start()

    # Yield elapsed-time-only updates while the thread is running (no ETA)
    while True:
        thread.join(timeout=1.0)
        elapsed = time.monotonic() - t0
        if not thread.is_alive():
            break
        yield (
            gr.update(),
            f"Running... {elapsed:.0f}s elapsed",
            gr.update(),
            gr.update(interactive=False, value=f"Running... ({int(elapsed)}s)"),
            _status_processing(f"Processing… elapsed: {int(elapsed)}s"),
        )

    # Thread finished — surface result or exception in the log
    elapsed = time.monotonic() - t0
    if result_bag[1] is not None:
        yield None, f"Error: {result_bag[1]}", _empty_output_info(), _BTN_IDLE, _status_fail(f"Failed after {elapsed:.1f}s")
        return

    out_path, log, info_html = result_bag[0]
    yield out_path, log, info_html, _BTN_IDLE, _status_done(f"Completed in {elapsed:.1f}s")


def _upscale_tab() -> gr.Tab:
    with gr.Tab("Upscale") as tab:
        gr.HTML(
            '<div class="workflow-hint">'
            '<span class="wf-step">Input</span>'
            '<span class="wf-arrow">→</span>'
            '<span class="wf-step">Real-ESRGAN</span>'
            '<span class="wf-arrow">→</span>'
            '<span class="wf-step">Post-process</span>'
            '<span class="wf-arrow">→</span>'
            '<span class="wf-step">Output</span>'
            '</div>'
        )
        with gr.Row():
            with gr.Column():
                img_in = gr.Image(label="Input image", type="filepath")
                in_info = gr.HTML(_empty_input_info())
            with gr.Column():
                img_out = gr.Image(label="Output preview", interactive=False)
                out_info = gr.HTML(_empty_output_info())
        with gr.Row():
            model = gr.Dropdown(
                choices=_UPSCALE_MODELS,
                value=_UPSCALE_MODELS[0],
                label="Model",
            )
            scale = gr.Dropdown(
                choices=["2", "4"],
                value="2",
                label="Scale",
            )
        with gr.Row():
            fmt = gr.Dropdown(
                choices=["png", "jpg", "webp"],
                value="png",
                label="Output format",
            )
            quality = gr.Slider(50, 100, value=90, step=1, label="Quality (JPEG / WebP)")
        face_enhance = gr.Checkbox(
            label="Face enhance",
            value=False,
            info="Applies face restoration. Only available with the Python script backend.",
        )
        with gr.Accordion("Post-processing options", open=False):
            auto_compress = gr.Checkbox(
                label="Auto-compress after upscale",
                value=False,
                info="Run a compression pass on the output before saving.",
            )
            with gr.Row():
                max_width = gr.Dropdown(
                    choices=list(MAX_WIDTHS.keys()),
                    value="original",
                    label="Max width",
                )
                target_size = gr.Dropdown(
                    choices=list(TARGET_SIZES.keys()),
                    value="none",
                    label="Target max file size",
                )
        _saved_realesrgan_path = load_local_config().get("realesrgan_path", "")
        backend_path_input = gr.Textbox(
            label="Real-ESRGAN path",
            placeholder="/path/to/Real-ESRGAN  or  /path/to/realesrgan-ncnn-vulkan",
            info="Optional. Leave empty to auto-detect or use REAL_ESRGAN_PATH.",
            value=_saved_realesrgan_path,
        )
        run_btn = gr.Button("Run Upscale", variant="primary")
        status_out = gr.HTML("")
        log_out = gr.Textbox(label="Log", interactive=False, lines=5)

        img_in.change(fn=_input_image_info, inputs=img_in, outputs=in_info)
        run_btn.click(
            fn=_do_upscale,
            inputs=[backend_path_input, img_in, scale, model, face_enhance, fmt, quality, auto_compress, max_width, target_size],
            outputs=[img_out, log_out, out_info, run_btn, status_out],
            show_progress="hidden",
        )
    return tab


# ── Compress tab ──────────────────────────────────────────────────────────────

def _do_compress(
    img_path: str | None,
    fmt: str,
    quality: int,
    max_width_str: str,
    target_size_str: str,
    strip_meta: bool,
) -> tuple[str | None, str, str]:
    if not img_path:
        return None, "No input image provided.", _empty_output_info()

    input_path = Path(img_path)
    out_name = timestamped_filename(input_path.stem, f".{fmt}")

    try:
        output_path = safe_output_path(OUTPUTS["compressed"], out_name)
    except FileExistsError as exc:
        return None, str(exc), _empty_output_info()

    try:
        result = compress_image(
            input_path=input_path,
            output_path=output_path,
            fmt=fmt,
            quality=quality,
            max_width=MAX_WIDTHS.get(max_width_str),
            target_bytes=TARGET_SIZES.get(target_size_str),
            strip_metadata=strip_meta,
        )
    except Exception as exc:
        return None, f"Error: {exc}", _empty_output_info()

    in_kb = result["input_size"] / 1024
    out_kb = result["output_size"] / 1024
    ratio = out_kb / in_kb if in_kb > 0 else 1.0
    log = (
        f"Saved:  {result['output_path']}\n"
        f"Before: {in_kb:.1f} KB  →  After: {out_kb:.1f} KB\n"
        f"{result['log']}"
    )
    ratio_cls = "good" if ratio < 1.0 else ""
    info_html = _info_card_html([
        ("Input", f"{in_kb:.1f} KB", ""),
        ("Output", f"{out_kb:.1f} KB", ""),
        ("Ratio", f"{ratio * 100:.0f}%", ratio_cls),
        ("Format", fmt.upper(), "dim"),
    ])
    return str(result["output_path"]), log, info_html


def _compress_tab() -> gr.Tab:
    with gr.Tab("Compress / Resize") as tab:
        gr.HTML(
            '<div class="workflow-hint">'
            '<span class="wf-step">Input</span>'
            '<span class="wf-arrow">→</span>'
            '<span class="wf-step">Resize</span>'
            '<span class="wf-arrow">→</span>'
            '<span class="wf-step">Compress</span>'
            '<span class="wf-arrow">→</span>'
            '<span class="wf-step">Output</span>'
            '</div>'
        )
        with gr.Row():
            with gr.Column():
                img_in = gr.Image(label="Input image", type="filepath")
                in_info = gr.HTML(_empty_input_info())
            with gr.Column():
                img_out = gr.Image(label="Output preview", interactive=False)
                out_info = gr.HTML(_empty_output_info())
        with gr.Row():
            fmt = gr.Radio(
                ["jpg", "png", "webp"],
                value="jpg",
                label="Output format",
            )
            quality = gr.Slider(1, 100, value=80, step=1, label="Quality (JPEG / WebP)")
        with gr.Row():
            max_width = gr.Dropdown(
                choices=list(MAX_WIDTHS.keys()),
                value="original",
                label="Max width",
                info="Downsample if the image exceeds this width.",
            )
            target_size = gr.Dropdown(
                choices=list(TARGET_SIZES.keys()),
                value="none",
                label="Target file size",
                info="Iteratively reduce quality until the file is under this limit.",
            )
        strip_meta = gr.Checkbox(
            label="Strip metadata (EXIF etc.)",
            value=False,
            info="Remove embedded metadata to reduce file size and privacy exposure.",
        )
        run_btn = gr.Button("Compress / Resize", variant="primary")
        log_out = gr.Textbox(label="Log", interactive=False, lines=4)

        img_in.change(fn=_input_image_info, inputs=img_in, outputs=in_info)
        run_btn.click(
            fn=_do_compress,
            inputs=[img_in, fmt, quality, max_width, target_size, strip_meta],
            outputs=[img_out, log_out, out_info],
            show_progress="hidden",
        )
    return tab


# ── Batch tab ─────────────────────────────────────────────────────────────────

def _batch_tab() -> gr.Tab:
    with gr.Tab("Batch Folder Mode") as tab:
        gr.HTML(
            '<div class="workflow-hint">'
            '<span class="wf-step">Input folder</span>'
            '<span class="wf-arrow">→</span>'
            '<span class="wf-step">Process all</span>'
            '<span class="wf-arrow">→</span>'
            '<span class="wf-step">Output folder</span>'
            '</div>'
            '<div class="batch-coming-soon">Full batch implementation coming soon.</div>'
        )
        folder = gr.Textbox(
            label="Input folder path",
            placeholder="/path/to/images",
            info="Absolute path to the folder containing images to process.",
        )
        run_btn = gr.Button("Run Batch", variant="primary")
        output = gr.Textbox(label="Result", interactive=False, lines=4)
        run_btn.click(
            fn=lambda _folder: placeholder_result("Batch"),
            inputs=folder,
            outputs=output,
        )
    return tab


# ── Entry point ───────────────────────────────────────────────────────────────

def build_ui() -> gr.Blocks:
    with gr.Blocks(
        title="pixctl",
    ) as demo:
        gr.HTML(_build_header_html())
        _upscale_tab()
        _compress_tab()
        _batch_tab()
    return demo
