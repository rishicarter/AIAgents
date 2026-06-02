import easyocr

reader = easyocr.Reader(['en'])

results = reader.readtext("./page_0.jpg")
all_text = ""
for result in results:
    all_text += result[1] + "\n"

print(all_text)