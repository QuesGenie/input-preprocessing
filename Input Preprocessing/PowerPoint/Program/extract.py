import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
from PIL import Image
import io
from preprocessing import *
import os




def extract_text_from_image(image_blob, relevance_model, labels):
    try:
        image = Image.open(io.BytesIO(image_blob))
        text = pytesseract.image_to_string(image)
        text_pre = preprocess_text(text.strip())
        if text_pre and is_relevant_text(text_pre, relevance_model, labels):
            return text_pre
        return None
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None



def extract_all_text(ppt):
    all_text = []
    for slide in ppt.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text_frame.text.strip()
                if text:
                    preprocessed_text = preprocess_text(text)
                    if preprocessed_text:
                        all_text.append(preprocessed_text)
    return all_text