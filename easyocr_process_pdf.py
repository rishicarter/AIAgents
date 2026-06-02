from pdf2image import convert_from_path
import easyocr
from io import BytesIO

def pdf_reader_with_easyocr(file_loc: str):
    reader = easyocr.Reader(['en'])

    pages = convert_from_path(file_loc)

    all_text = ""

    for _, page in enumerate(pages):

        raw_page = BytesIO()
        page.save(raw_page, format="JPEG")

        results = reader.readtext(raw_page.getvalue())
        for result in results:
            all_text += result[1] + "\n"

    print(all_text)

# def real_pdf():
#     reader = easyocr.Reader(['en'])

#     pages = convert_from_path("images/invoice1.pdf")

#     all_text = ""

#     for page_num, page in enumerate(pages):
#         raw_page = BytesIO()
#         page.save(raw_page, format="JPEG")

#         results = reader.readtext(raw_page.getvalue())
#         for result in results:
#             all_text += result[1] + "\n"

#     print(all_text)

if __name__ == "__main__":
    IMG_PATH = "images/invoice1.pdf"
    IMG_PATH2 = "images/invoice2.pdf"
    pdf_reader_with_easyocr(IMG_PATH2)