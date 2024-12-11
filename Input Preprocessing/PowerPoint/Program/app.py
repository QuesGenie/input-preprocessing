from pptx import Presentation
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
import json
import time
import uuid
from extract import *
from candidate_labels import * 
import shutil


def write_json_to_file(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
            print(f"JSON data has been written to {filename}")
    except Exception as e:
            print(f"An error occurred while writing JSON to file: {e}")


def PowerPointExtractor(path, relevance_model):
    # Folder path
    folder_name = path.split('/')[-1].split('.')[0] + str(uuid.uuid4())
    folder_path = os.path.join('Data', folder_name)
    folder_image_path = os.path.join(folder_path, 'Images')
    folder_text_path = os.path.join(folder_path, 'Text')

    stats = {
        "total_slides": 0,
        "total_images_extracted": 0,
        "total_relevant_text_blocks": 0,
        "total_ocr_text_blocks": 0,
        "processing_time": 0,
    }

    try:
        os.makedirs(folder_image_path, exist_ok=True)
        os.makedirs(folder_text_path, exist_ok=True)

        extracted_content = {"slides": []}
        ppt = Presentation(path)
        stats["total_slides"] = len(ppt.slides)

        # Extract all text from slides for topic modeling
        all_text = extract_all_text(ppt)

        labels = generate_candidate_labels(all_text)
        lable_encoding = relevance_model.encode(labels)
        slide_number = 1

        start_time = time.time()  # Start timing
        for slide in tqdm(ppt.slides):
            slide_data = {"slide_number": slide_number, "content": []}
            index = 1

            for shape in slide.shapes:
                if shape.has_text_frame and shape.text_frame.text.strip():
                    text = shape.text_frame.text.strip()
                    preprocessed_text = preprocess_text(text)
                    if preprocessed_text and is_relevant_text(preprocessed_text, relevance_model, lable_encoding):
                        slide_data["content"].append({
                            "type": "text",
                            "text": text,
                        })
                        stats["total_relevant_text_blocks"] += 1

                elif hasattr(shape, "image"):
                    image_data = shape.image.blob
                    # Extract text from the image
                    ocr_text = extract_text_from_image(image_data, relevance_model, lable_encoding)
                    image_path = os.path.join(folder_image_path, f"image_{slide_number}_{index}.png")
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    if not ocr_text:
                        slide_data["content"].append({
                            "type": "image",
                            "placeholder": f"[Image {slide_number}_{index}]",
                            "image_path": image_path
                        })
                        stats["total_images_extracted"] += 1
                        index += 1
                    else:
                        slide_data["content"].append({
                            "type": "image",
                            "placeholder": f"[Image {slide_number}_{index}]",
                            "image_path": image_path,
                            "ocr_text": ocr_text 
                        })
                        stats["total_ocr_text_blocks"] += 1
                        index += 1

            if slide_data["content"]:
                extracted_content["slides"].append(slide_data)
            slide_number += 1

        file_name = os.path.join(folder_text_path, f'Data-{folder_name}.json')
        write_json_to_file(extracted_content, file_name)

        
        stats["processing_time"] = time.time() - start_time

        
        print("\n=== PowerPoint Extraction Stats ===")
        print(f"Total Slides: {stats['total_slides']}")
        print(f"Processing Time: {stats['processing_time']:.2f} seconds")
        print(f"Total Images Extracted: {stats['total_images_extracted']}")
        print(f"Total Relevant Text Blocks: {stats['total_relevant_text_blocks']}")
        print(f"Total OCR Text Blocks: {stats['total_ocr_text_blocks']}")

        return file_name
    except Exception as e:
        print(f"An error occurred while processing the PowerPoint: {e}")
        # Delete the folder if an error has occurred
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"Deleted created folders: {folder_path}")


if __name__ == "__main__":
    relevance_model = SentenceTransformer('all-MiniLM-L6-v2')
    file_name = PowerPointExtractor('./_lec9.pptx',relevance_model)