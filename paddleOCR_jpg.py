from paddleocr import PaddleOCR

ocr = PaddleOCR(enable_mkldnn=False)

results = ocr.predict("./page_0.jpg")

full_text = ""

for page in results:
    full_text += "\n".join(page["rec_texts"])

print(full_text)