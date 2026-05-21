from pathlib import Path

import gradio as gr
from PIL import Image as PILImage

from src.config import OUTPUTS, TEMP_DIR
from src.image_ops import MAX_WIDTHS, TARGET_SIZES, compress_image
from src.realesrgan_runner import Backend, detect_backend, run_upscale
from src.utils import placeholder_result, safe_output_path, timestamped_filename

_UPSCALE_MODELS = [
    "realesrgan-x4plus",
    "realesrgan-x4plus-anime",
    "realesr-animevideov3",
]

_UPSCALE_MAX_WIDTHS: dict[str, int | None] = {
    "original": None,
    "1920": 1920,
    "2560": 2560,
    "3840": 3840,
}

_UPSCALE_TARGET_SIZES: dict[str, int | None] = {
    "none": None,
    "2MB": 2 * 1024 * 1024,
    "5MB": 5 * 1024 * 1024,
    "10MB": 10 * 1024 * 1024,
}

_CUSTOM_CSS = """
/* ── pixctl premium dark theme ── */

body, .gradio-container {
    font-family: 'Inter', 'SF Pro Display', ui-sans-serif, system-ui, -apple-system, sans-serif !important;
}

/* Tab navigation */
.tab-nav {
    border-bottom: 1px solid #2a2e45 !important;
    margin-bottom: 10px !important;
}
.tab-nav button {
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    border-radius: 6px 6px 0 0 !important;
    transition: color 0.15s, background 0.15s !important;
}

/* Log / Textbox monospace */
textarea {
    font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', 'Cascadia Code', monospace !important;
    font-size: 11.5px !important;
    line-height: 1.65 !important;
}

/* Slider accent */
input[type="range"] {
    accent-color: #818cf8 !important;
}

/* ── Custom HTML components ── */

/* Header card */
.pixctl-header {
    background: linear-gradient(135deg, #1a1d2e 0%, #1e2235 100%);
    border: 1px solid #2a2e45;
    border-radius: 12px;
    padding: 18px 22px 14px;
    margin-bottom: 2px;
}
.pixctl-header h1 {
    margin: 0 0 3px;
    font-size: 21px;
    font-weight: 800;
    letter-spacing: -0.4px;
    color: #e2e8f8;
    line-height: 1.2;
}
.pixctl-header .tagline {
    font-size: 12px;
    color: #5a6080;
    margin-bottom: 10px;
}

/* Backend badge */
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
    background: rgba(34, 197, 94, 0.1);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.2);
}
.backend-none {
    background: rgba(251, 146, 60, 0.08);
    color: #fb923c;
    border: 1px solid rgba(251, 146, 60, 0.18);
}

/* Workflow hint strip */
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
    opacity: 0.7;
}
.wf-arrow {
    font-size: 12px;
    opacity: 0.4;
}

/* Info card */
.info-card {
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px 20px;
    margin-top: 4px;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(0,0,0,0.15);
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
    opacity: 0.5;
}
.info-metric-value {
    font-size: 13px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}
.info-metric-value.dim { opacity: 0.35; }
.info-metric-value.good { color: #4ade80; }
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


# ── Backend status ─────────────────────────────────────────────────────────────

def _backend_status_html(backend: Backend) -> str:
    if backend.available:
        label = "ncnn-vulkan" if backend.kind == "ncnn" else "Python script"
        path_short = Path(backend.path).name
        return (
            f'<span class="backend-badge backend-ok">'
            f'● {label} · {path_short}'
            f'</span>'
        )
    return (
        '<span class="backend-badge backend-none">'
        '⚠ No backend · upscale unavailable'
        '</span>'
    )


def _build_header_html(backend: Backend) -> str:
    badge = _backend_status_html(backend)
    return (
        '<div class="pixctl-header">'
        '<h1>pixctl</h1>'
        '<div class="tagline">Local image processing toolkit · AI upscale · compress · resize</div>'
        f'{badge}'
        '</div>'
    )


# ── Keep legacy markdown helper for any direct callers ────────────────────────

def _backend_status_md(backend: Backend) -> str:
    if backend.available:
        label = "ncnn-vulkan" if backend.kind == "ncnn" else "Python script"
        return f"**Backend:** {label} — `{backend.path}`"
    return (
        "**Backend:** No Real-ESRGAN backend found — upscaling unavailable. "
        "Compress and Batch tabs still work."
    )


# ── Upscale tab ───────────────────────────────────────────────────────────────

def _do_upscale(
    backend: Backend,
    img_path: str | None,
    scale_str: str,
    model: str,
    face_enhance: bool,
    fmt: str,
    quality: int,
    auto_compress: bool,
    max_width_str: str,
    target_size_str: str,
) -> tuple[str | None, str, str]:
    if not img_path:
        return None, "No input image provided.", _empty_output_info()
    if not backend.available:
        return None, (
            "No Real-ESRGAN backend found.\n"
            "Install realesrgan-ncnn-vulkan or place inference_realesrgan.py "
            "under ./Real-ESRGAN/."
        ), _empty_output_info()

    input_path = Path(img_path)
    scale = int(scale_str)
    input_size = input_path.stat().st_size

    tmp_name = timestamped_filename(f"{input_path.stem}_x{scale}_raw", ".png")
    tmp_path = TEMP_DIR / tmp_name

    result = run_upscale(
        backend,
        input_path,
        tmp_path,
        model=model,
        scale=scale,
        face_enhance=face_enhance,
    )

    if not result.success:
        lines = [f"Upscale failed (exit {result.returncode}, {result.duration:.1f}s)"]
        if result.stderr:
            lines.append(f"stderr: {result.stderr.strip()}")
        if result.stdout:
            lines.append(f"stdout: {result.stdout.strip()}")
        return None, "\n".join(lines), _empty_output_info()

    out_name = timestamped_filename(f"{input_path.stem}_x{scale}", f".{fmt}")
    try:
        output_path = safe_output_path(OUTPUTS["upscaled"], out_name)
    except FileExistsError as exc:
        if tmp_path.exists():
            tmp_path.unlink()
        return None, str(exc), _empty_output_info()

    target_bytes = _UPSCALE_TARGET_SIZES.get(target_size_str) if auto_compress else None
    max_width = _UPSCALE_MAX_WIDTHS.get(max_width_str) if auto_compress else None

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
        return None, f"Post-process error: {exc}", _empty_output_info()
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    in_kb = input_size / 1024
    out_kb = compress_result["output_size"] / 1024
    ratio = out_kb / in_kb if in_kb > 0 else 1.0
    log = (
        f"Done in {result.duration:.1f}s\n"
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
        ("Duration", f"{result.duration:.1f}s", "dim"),
    ])
    return str(compress_result["output_path"]), log, info_html


def _upscale_tab(backend: Backend) -> gr.Tab:
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
                    choices=list(_UPSCALE_MAX_WIDTHS.keys()),
                    value="original",
                    label="Max width",
                )
                target_size = gr.Dropdown(
                    choices=list(_UPSCALE_TARGET_SIZES.keys()),
                    value="none",
                    label="Target max file size",
                )
        run_btn = gr.Button("Run Upscale", variant="primary", interactive=backend.available)
        log_out = gr.Textbox(label="Log", interactive=False, lines=5)

        img_in.change(fn=_input_image_info, inputs=img_in, outputs=in_info)
        run_btn.click(
            fn=lambda img, sc, mdl, fe, f, q, ac, mw, ts: _do_upscale(
                backend, img, sc, mdl, fe, f, q, ac, mw, ts
            ),
            inputs=[img_in, scale, model, face_enhance, fmt, quality, auto_compress, max_width, target_size],
            outputs=[img_out, log_out, out_info],
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
        )
    return tab


# ── Batch tab ─────────────────────────────────────────────────────────────────

def _batch_tab() -> gr.Tab:
    with gr.Tab("Batch Folder Mode") as tab:
        gr.Markdown(
            "## Batch Folder Mode\n"
            "Process an entire folder of images at once. "
            "_Full implementation coming soon._"
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
    backend = detect_backend()
    with gr.Blocks(
        title="pixctl",
        theme=gr.themes.Ocean(),
        css=_CUSTOM_CSS,
    ) as demo:
        gr.HTML(_build_header_html(backend))
        _upscale_tab(backend)
        _compress_tab()
        _batch_tab()
    return demo
