import pdfplumber
import os
from input_preprocessing.documents.filters.extract import *
import input_preprocessing.documents.utils


class PDFPlumber:

    def extract_text_and_images(pdf_file):

        if not os.path.isfile(pdf_file):
            raise FileNotFoundError(f"The file '{pdf_file}' was not found.")
        else:
            print("Parsing", pdf_file)

        base_folder = os.path.splitext(pdf_file)[0]
        os.makedirs(base_folder, exist_ok=True)

        image_folder = os.path.join(base_folder, "img")
        os.makedirs(image_folder, exist_ok=True)
        slide = {"slide_number": page_number + 1, "content": []}
        extracted_content = {"slides": []}
        with pdfplumber.open(pdf_file) as pdf:
            for page_number, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                utils.add_text_to_json_format(text,page_number,slide)
                for i, img in enumerate(page.images):
                    ocr_text = TextExtractor.extract_text_from_image(img)
                    print("OCR:",ocr_text)
                    if not ocr_text:
                        image_filename = f"page_{page_number+1}_img_{i+1}.png"
                        image_path = os.path.join(image_folder, image_filename)
                        cropped_image = page.within_bbox((img["x0"], img["top"], img["x1"], img["bottom"])).to_image()
                        cropped_image.save(image_path)
                        utils.add_image_to_json_format(page_number,slide,{img,i,image_path})
                    else:
                        utils.add_image_text_to_json_format(slide,ocr_text)
                extracted_content["slides"].append(slide)
        return extracted_content
        
    