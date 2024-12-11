from pdf.pdf_extractor_controller import *
# AYA Look at this Example 🫡
controller = PDFExtractorController(Pymupdf())
pymupdf_output = controller.extract_text_and_images("pdf_path", "output_dir")
processed_json = controller.process_json_content(pymupdf_output)
processed_json = controller.process_json_images(pymupdf_output)
