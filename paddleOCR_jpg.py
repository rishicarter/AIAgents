from paddleocr import PaddleOCR
import cv2
import numpy as np

def preprocess_for_paddle(image_path):
    # 1. Load image
    img = cv2.imread(image_path)
    
    # 2. Resize if the image is too small or too large
    # PaddleOCR detects best when text height is roughly 20-40 pixels
    h, w = img.shape[:2]
    if max(h, w) > 2000:
        img = cv2.resize(img, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    elif max(h, w) < 500:
        img = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

    # 3. Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 4. Remove high-frequency noise while preserving sharp text edges
    # Bilateral filtering is much better than Gaussian Blur for OCR
    filtered = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    
    # 5. Fix uneven lighting and boost contrast using CLAHE
    # (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(filtered)
    
    # 6. Convert back to 3-channel BGR 
    # PaddleOCR expects a 3-channel color image input format
    final_img = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
    
    return final_img
processed_img = preprocess_for_paddle("./sample.jpeg")
# result = ocr.ocr(processed_img, cls=True)
ocr = PaddleOCR(
    use_doc_orientation_classify=True,
    use_doc_unwarping=True,
    use_textline_orientation=True,
    enable_mkldnn=False
)

results = ocr.predict(processed_img)

full_text = ""

for page in results:
    full_text += "\n".join(page["rec_texts"])

print(full_text)