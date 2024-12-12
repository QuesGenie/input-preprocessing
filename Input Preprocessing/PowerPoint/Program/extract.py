import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
from PIL import Image
import io
from preprocessing import *
import os


class TextExtractor:
    @staticmethod
    def extract_text_from_image(image_blob, relevance_model, label_embeddings):
        try:
            image = Image.open(io.BytesIO(image_blob))
            text = pytesseract.image_to_string(image).strip()
            preprocessed_text = TextPreprocessor.preprocess_text(text)
            if preprocessed_text and TextPreprocessor.is_relevant_text(preprocessed_text, relevance_model, label_embeddings):
                return preprocessed_text
            return None
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return None

    @staticmethod
    def extract_all_text(ppt):
        all_text = []
        for slide in ppt.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text = shape.text_frame.text.strip()
                    preprocessed_text = TextPreprocessor.preprocess_text(text)
                    if preprocessed_text:
                        all_text.append(preprocessed_text)
        return all_text




