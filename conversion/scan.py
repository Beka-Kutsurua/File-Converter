import easyocr
import os

reader = easyocr.Reader(['en'])

def extract_text(image_path):
    try:
        results = reader.readtext(image_path)
        extracted = '\n'.join([line[1] for line in results])
        return extracted
    except Exception as e:
        return f"Error during OCR: {str(e)}"
