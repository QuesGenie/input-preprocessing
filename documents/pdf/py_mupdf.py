import pymupdf
import os
from tqdm.auto import tqdm

class Pymupdf:
    def extract_text_and_images(self,pdf_path, output_dir):

        pdf_document = pymupdf.open(pdf_path)

        slides = []

        for page_number in tqdm(range(len(pdf_document))):
            page = pdf_document[page_number]
            slide_content = []

            text = page.get_text("text")
            if text.strip():
                slide_content.append({"type": "text", "text": text.strip()})

            images = page.get_images(full=True)
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                image_filename = f"page{page_number + 1}_image{img_index + 1}.{image_ext}"
                image_path = os.path.join(output_dir, image_filename)
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                slide_content.append({
                    "type": "image",
                    "placeholder": f"[Image {img_index + 1}]",
                    "image_path": image_path
                })

            slides.append({
                "page_number": page_number + 1,
                "content": slide_content
            })

        pdf_document.close()

        result = {"pages": slides}
        return result
