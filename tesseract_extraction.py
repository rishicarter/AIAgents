import cv2
import pytesseract

img = cv2.imread("./sample.jpeg")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# thresh = cv2.threshold(
#     gray,
#     0,
#     255,
#     cv2.THRESH_BINARY + cv2.THRESH_OTSU
# )[1]
text = pytesseract.image_to_string(
    # thresh,
    gray,
    config='--psm 6'
)


print(text)