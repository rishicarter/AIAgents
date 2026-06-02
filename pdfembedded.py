import fitz

IMG_PATH = "images/invoice1.pdf"
IMG_PATH2 = "images/invoice2.pdf"

docs = fitz.open(IMG_PATH2)
print(len(docs), type(docs))
for pn in range(len(docs)):
    print(len(docs[pn]))
    page = docs[pn]

    text = page.get_text()

    print(text)