import os

os.environ["FLAGS_use_mkldnn"] = "0"

from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_doc_orientation_classify=True,
    use_doc_unwarping=True,
    use_textline_orientation=True,
    enable_mkldnn=False
)

results = ocr.predict("images/invoice1.pdf")

for page in results:

    for text in page['rec_texts']:
        print(text)