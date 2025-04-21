# conversion/scan.py
import easyocr
import os

# Initialize reader once (outside function to avoid reloading every call)
reader = easyocr.Reader(['en'])  # Add more languages if needed

def extract_text(image_path):
    try:
        results = reader.readtext(image_path)
        extracted = '\n'.join([line[1] for line in results])
        return extracted
    except Exception as e:
        return f"Error during OCR: {str(e)}"
