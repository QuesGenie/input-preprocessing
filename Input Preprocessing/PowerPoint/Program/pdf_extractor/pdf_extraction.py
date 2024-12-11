from pdf_plumber_processor import PDFPlumperProcessor
from utils import utils
class  pdf_extractor:
    extracted_content= PDFPlumperProcessor.extract_text_and_images()
    # utils.write_json_to_file(extracted_content,)
    
