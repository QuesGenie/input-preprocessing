import pytesseract
from PIL import Image
from preprocessing import *
import os




def extract_text_from_image(image_blob):
    try:
        with open("temp_image.png", "wb") as temp_image_file:
            temp_image_file.write(image_blob)
        image = Image.open("temp_image.png")
        text = pytesseract.image_to_string(image)
        os.remove("temp_image.png")  # Clean up temp image
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None



def extract_all_text(ppt):
    """Extract all text from the presentation for topic modeling."""
    all_text = []
    for slide in ppt.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text_frame.text.strip()
                if text:
                    preprocessed_text = preprocess_text(text)
                    if preprocessed_text:
                        all_text.append(preprocessed_text)
            elif hasattr(shape, "image"):
                image_text = extract_text_from_image(shape.image.blob)
                if image_text:
                    all_text.append(image_text)
    return all_text