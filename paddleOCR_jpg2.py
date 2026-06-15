from __future__ import annotations

from pathlib import Path
from typing import Union, Tuple, Optional

import cv2
import numpy as np

from paddleocr import PaddleOCR


def preprocess_image_for_llm(
    image: Union[str, Path, np.ndarray],
    target_width: int = 2000,
    jpeg_quality: int = 80,
    output_format: str = "webp",
    save_path: Optional[Union[str, Path]] = None,
) -> Tuple[np.ndarray, Optional[bytes]]:
    """
    Single-function document preprocessing for OCR/LLM extraction.

    Covers:
    1) crop margins / whitespace
    2) grayscale
    3) deskew
    4) resize to target width
    5) JPEG compression
    6) WebP compression

    Parameters
    ----------
    image:
        Path to image or already-loaded BGR/gray NumPy array.
    target_width:
        Resize long edge down to this width if larger.
    jpeg_quality:
        Used when output_format == "jpg" or "jpeg".
    output_format:
        "jpg", "jpeg", or "webp".
    save_path:
        Optional file path to save the compressed result.

    Returns
    -------
    processed_image:
        Final preprocessed grayscale image as NumPy array.
    encoded_bytes:
        Encoded image bytes if save_path is None, else None.
    """

    # ---------- load ----------
    if isinstance(image, (str, Path)):
        img = cv2.imread(str(image), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Could not read image: {image}")
    elif isinstance(image, np.ndarray):
        img = image.copy()
    else:
        raise TypeError("image must be a file path or a NumPy array")
    print(img.shape)
    # ---------- grayscale ----------
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # ---------- crop whitespace / margins ----------
    # Invert threshold so content becomes white on black, then find content bbox.
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    coords = cv2.findNonZero(th)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        pad = max(5, int(0.02 * max(w, h)))
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(gray.shape[1], x + w + pad)
        y2 = min(gray.shape[0], y + h + pad)
        gray = gray[y1:y2, x1:x2]

    # ---------- deskew ----------
    # Estimate angle from foreground pixels.
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = cv2.findNonZero(th)

    if coords is not None and len(coords) > 50:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]

        # cv2.minAreaRect angle is in [-90, 0); adjust to a usable skew angle.
        if angle < -45:
            angle = 90 + angle
        else:
            angle = angle

        # Skip tiny rotations.
        if abs(angle) > 0.5:
            (h, w) = gray.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            gray = cv2.warpAffine(
                gray,
                M,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            )

    # ---------- resize ----------
    h, w = gray.shape[:2]
    if w > target_width:
        scale = target_width / float(w)
        new_w = target_width
        new_h = max(1, int(h * scale))
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # ---------- encode / compress ----------
    ext = output_format.lower().strip()
    if ext == "jpeg":
        ext = "jpg"

    if ext not in {"jpg", "webp"}:
        raise ValueError("output_format must be 'jpg', 'jpeg', or 'webp'")

    params = []
    if ext == "jpg":
        params = [cv2.IMWRITE_JPEG_QUALITY, int(jpeg_quality)]
    elif ext == "webp":
        params = [cv2.IMWRITE_WEBP_QUALITY, int(jpeg_quality)]

    ok, encoded = cv2.imencode(f".{ext}", gray, params)
    if not ok:
        raise RuntimeError("Image encoding failed")

    encoded_bytes = encoded.tobytes()

    # ---------- optional save ----------
    if save_path is not None:
        save_path = Path(save_path)
        save_path.write_bytes(encoded_bytes)
        return gray, None

    return gray, encoded_bytes

processed_img, image_bytes = preprocess_image_for_llm(image="./s1.jpeg", save_path="t2.jpeg")
# result = ocr.ocr(processed_img, cls=True)
print(processed_img.shape, type(processed_img))
ocr = PaddleOCR(
    use_doc_orientation_classify=True,
    use_doc_unwarping=True,
    use_textline_orientation=True,
    enable_mkldnn=False
)
processed_img = np.expand_dims(processed_img, axis=-1)
results = ocr.predict(processed_img)

full_text = ""

for page in results:
    full_text += "\n".join(page["rec_texts"])

print(full_text)