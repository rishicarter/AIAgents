"""
ocr_pipeline.py
---------------
Production-grade OCR pipeline using PaddleOCR (CPU) with image preprocessing.

Install dependencies:
    pip install paddlepaddle paddleocr pillow opencv-python-headless numpy

Usage:
    from ocr_pipeline import run_ocr

    results = run_ocr("photo.jpg")
    for item in results:
        print(item["text"], item["confidence"])
"""

import cv2
import logging
import numpy as np
from pathlib import Path
from PIL import Image, ImageOps
from dataclasses import dataclass, field
from typing import Optional

# ─── Config ───────────────────────────────────────────────────────────────────

MAX_LONG_SIDE: int = 800    # Resize longest dimension to this (px). Reduces RAM ~2-4x.
                             # Safe floor for PaddleOCR legibility: 640. Max recommended: 1280.
MIN_LONG_SIDE: int = 640    # Never downsample below this (avoids blurring small text).
CONF_THRESHOLD: float = 0.5 # Discard detections below this confidence score.

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("ocr_pipeline")

# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class OCRResult:
    text: str
    confidence: float
    bbox: list[list[int]]   # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] in resized-image coords

@dataclass
class OCROutput:
    results: list[OCRResult] = field(default_factory=list)
    full_text: str = ""
    image_shape: tuple[int, int] = (0, 0)   # (H, W) of the preprocessed image
    source_shape: tuple[int, int] = (0, 0)  # (H, W) of the original image

# ─── Lazy singleton for the PaddleOCR model ───────────────────────────────────

_ocr_instance = None

def _get_ocr():
    """
    Initialise PaddleOCR once and reuse across calls.
    CPU-only: use_gpu=False, use_angle_cls=True (handles rotated text).
    """
    global _ocr_instance
    if _ocr_instance is None:
        try:
            from paddleocr import PaddleOCR
        except ImportError as e:
            raise ImportError(
                "PaddleOCR is not installed. Run:\n"
                "  pip install paddlepaddle paddleocr"
            ) from e

        log.info("Initialising PaddleOCR (CPU) — first call downloads model weights (~30 MB).")
        _ocr_instance = PaddleOCR(
            use_textline_orientation=True,   # Correct 90°/180°/270° text rotation
            lang="en",            # Change to "ch", "hi", etc. for other languages
            # use_gpu=False,        # CPU inference
            # show_log=False,       # Suppress PaddlePaddle verbose output
            enable_mkldnn=False,   # Intel MKL-DNN acceleration on x86 CPUs (free perf boost)
        )
        log.info("PaddleOCR ready.")
    return _ocr_instance


# ─── Preprocessing ────────────────────────────────────────────────────────────

def _preprocess(image_path: str | Path) -> tuple[np.ndarray, tuple[int, int]]:
    """
    Load and preprocess an image for PaddleOCR:
      1. EXIF-aware load  → corrects phone/camera auto-rotation (portrait vs landscape).
      2. RGB conversion   → strips alpha channel, normalises colour space.
      3. Smart resize     → shrinks high-res inputs to MAX_LONG_SIDE on the longest axis,
                            keeping aspect ratio. Never upscales small images.
                            Uses INTER_AREA (best quality for downsampling).

    Returns:
        img_rgb  : preprocessed uint8 NumPy array (H, W, 3) ready for PaddleOCR.
        orig_hw  : (H, W) of the original image before resizing.
    """
    # --- 1. Load & honour EXIF rotation ---
    pil_img = Image.open(image_path)
    pil_img = ImageOps.exif_transpose(pil_img)  # Rotates in-memory; no quality loss

    # --- 2. Ensure RGB (drop alpha, handle palette/grayscale) ---
    img_rgb = np.array(pil_img.convert("RGB"), dtype=np.uint8)
    orig_hw = img_rgb.shape[:2]   # (H, W)
    h, w = orig_hw

    # --- 3. Resize: longest side → MAX_LONG_SIDE (only downscale) ---
    long_side = max(h, w)
    if long_side > MAX_LONG_SIDE:
        scale = MAX_LONG_SIDE / long_side
        new_h = max(int(h * scale), MIN_LONG_SIDE if h >= w else 1)
        new_w = max(int(w * scale), MIN_LONG_SIDE if w > h else 1)
        img_rgb = cv2.resize(img_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        log.info(
            "Resized %dx%d → %dx%d  (%.1fx RAM reduction)",
            w, h, new_w, new_h,
            (h * w) / (new_h * new_w),
        )
    else:
        log.info("Image %dx%d is within limits — no resize needed.", w, h)

    return img_rgb, orig_hw


# ─── Main entry point ─────────────────────────────────────────────────────────

def run_ocr(
    image_path: str | Path,
    conf_threshold: Optional[float] = None,
) -> OCROutput:
    """
    Run the full OCR pipeline on a JPEG (or any PIL-readable image).

    Args:
        image_path      : Path to the input image.
        conf_threshold  : Minimum confidence to keep a detection (default: CONF_THRESHOLD).

    Returns:
        OCROutput with:
          .results    — list of OCRResult (text, confidence, bbox)
          .full_text  — all detected text joined by newlines (reading order, top→bottom)
          .image_shape — (H, W) of the preprocessed image fed to PaddleOCR
          .source_shape — (H, W) of the original image

    Example:
        output = run_ocr("note.jpg")
        print(output.full_text)
        for r in output.results:
            print(f"  [{r.confidence:.2f}] {r.text}")
    """
    threshold = conf_threshold if conf_threshold is not None else CONF_THRESHOLD
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # ── Preprocess ──────────────────────────────────────────────────────────
    img_rgb, orig_hw = _preprocess(image_path)

    # ── Inference ───────────────────────────────────────────────────────────
    ocr = _get_ocr()
    log.info("Running OCR on shape %s …", img_rgb.shape)
    raw = ocr.predict(img_rgb)

    # ── Parse results ────────────────────────────────────────────────────────
    output = OCROutput(
        image_shape=img_rgb.shape[:2],
        source_shape=orig_hw,
    )

    if not raw or raw[0] is None:
        log.warning("PaddleOCR returned no detections.")
        return output

    lines: list[str] = []
    for detection in raw[0]:            # raw[0] = list of [bbox, (text, score)]
        bbox, (text, score) = detection
        if score < threshold:
            log.debug("Skipping '%s' (conf=%.2f < %.2f)", text, score, threshold)
            continue
        bbox_int = [[int(x), int(y)] for x, y in bbox]
        output.results.append(OCRResult(text=text, confidence=round(score, 4), bbox=bbox_int))
        lines.append(text)

    # Sort top-to-bottom by the y-coordinate of the top-left corner of each bbox
    output.results.sort(key=lambda r: r.bbox[0][1])
    output.full_text = "\n".join(r.text for r in output.results)

    log.info("Detected %d text region(s).", len(output.results))
    return output


# ─── CLI helper ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <image_path>")
        sys.exit(1)

    out = run_ocr(sys.argv[1])

    print("\n── Full Text ──────────────────────────────────")
    print(out.full_text)

    print("\n── Detections ─────────────────────────────────")
    for r in out.results:
        print(f"  [{r.confidence:.2f}]  {r.text}")
        print(f"           bbox: {r.bbox}")

    print(f"\nSource image : {out.source_shape[1]}x{out.source_shape[0]} px")
    print(f"Processed    : {out.image_shape[1]}x{out.image_shape[0]} px")