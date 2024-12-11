import pymupdf
import os
import json

def extract_text_and_images(pdf_path, output_dir):
    """
    Extracts text and images from a PDF and formats them into the desired JSON structure.

    Args:
        pdf_path (str): Path to the PDF file.
        output_dir (str): Directory where extracted images will be saved.

    Returns:
        dict: JSON structure with extracted text and image placeholders.
    """
    os.makedirs(output_dir, exist_ok=True)

    pdf_document = pymupdf.open(pdf_path)

    slides = []

    for page_number in range(len(pdf_document)):
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
            "slide_number": page_number + 1,
            "content": slide_content
        })

    pdf_document.close()

    result = {"slides": slides}
    return result


# extracted_data = extract_text_and_images("/content/[IoT'24] Lecture 2.pdf", "/content/extracted_pdf")

# with open("extracted_data.json", "w", encoding="utf-8") as json_file:
#   json.dump(extracted_data, json_file, indent=4, ensure_ascii=False)
#   print("Extraction complete. Data saved to extracted_data.json")
