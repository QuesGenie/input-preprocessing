import os
import json

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
