import os
import json
from PowerPoint.preprocessing import *
from utils.extract import *

class PDFExtractorController:
    def __init__(self, extractor):
        """
        Args:
            extractor (Object): The tool to use for PDF extraction. Options: Pymupdf(), Plumber().
        """
        self.extractor = extractor
    
    def extract_text_and_images(self, pdf_path, output_dir):
        """
        Delegates text and image extraction to the selected tool.

        Args:
            pdf_path (str): Path to the PDF file.
            output_dir (str): Directory where extracted images will be saved.

        Returns:
            dict: JSON structure with extracted text and image placeholders.
        """
        return self.extractor.extract_text_and_images(pdf_path, output_dir)
    
    def process_json_content(json_data, relevance_model, labels):
        for slide in json_data.get("slides", []):
            updated_content = []
            for content in slide.get("content", []):
                if content.get("type") == "text":
                    original_text = content.get("text", "")
                    original_text = preprocess_text(original_text)
                    if is_relevant_text(original_text, relevance_model, labels):
                        content["text"] = original_text
                        updated_content.append(content)
                else:
                    updated_content.append(content)

            slide["content"] = updated_content
        return json_data

    def process_json_images(json_data):
        for slide in json_data.get("slides", []):
            updated_content = []
            for content in slide.get("content", []):
                if content.get("type") == "image":
                    path = content.get("image_path", "")
                    ocr_txt  = extract_text_from_image(path)
                    if ocr_text:
                        processed_text = preprocess_text(ocr_text)
                        if is_relevant_text(processed_text, relevance_model, labels):
                            content  =  { "type": "image","ocr_text": processed_text}
                            updated_content.append(content)
                else:
                    updated_content.append(content)

            slide["content"] = updated_content
        return json_data
