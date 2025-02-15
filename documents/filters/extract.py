import pytesseract
from PIL import Image
import io
import os


class TextExtractor:
    @staticmethod
    def extract_text_from_image(image_blob):
        try:
            image = Image.open(io.BytesIO(image_blob))
            text = pytesseract.image_to_string(image).strip()
            return text
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
                    all_text.append(text)
        return all_text
    
    
        




