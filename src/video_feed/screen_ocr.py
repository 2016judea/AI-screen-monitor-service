from PIL import Image
import pytesseract

def extract_text(img: Image.Image) -> str:
    text = pytesseract.image_to_string(img)
    # Optional: clean up text
    text = text.strip()
    return text
