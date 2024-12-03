from pptx import Presentation
from transformers import pipeline
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import json
import os
import uuid


def is_relevant_text(text, relevance_model):
    try:
        candidate_labels = ["educational content", "lecture", "topic", "key point","questions","Explanation"]
        result = relevance_model(text, candidate_labels=candidate_labels)
        return max(result["scores"]) > 0.5
    except Exception as e:
        print(f"Error with relevance model: {e}")
        return False


def PreprocessTheText(text,relevance_model):
  new_text = text.lower().translate(str.maketrans("", "", string.punctuation))
  stop_words = set(stopwords.words("english"))
  tokens = [word for word in new_text.split() if word not in stop_words]
  if not tokens or len(tokens) < 10:
    return None
  if relevance_model and not is_relevant_text(" ".join(tokens), relevance_model):
        return None
  return text


def write_json_to_file(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"JSON data has been written to {filename}")
    except Exception as e:
        print(f"An error occurred while writing JSON to file: {e}")



def PowerPointExtractor(Path,relevance_model):

    folder_name = Path.split('/')[-1].split('.')[0] + str(uuid.uuid4())
    folder_path = os.path.join('Data',folder_name)
    folder_image_path = os.path.join(folder_path,'Images')
    folder_Text_path = os.path.join(folder_path,'Text')

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if not os.path.exists(folder_image_path):
        os.makedirs(folder_image_path)

    if not os.path.exists(folder_Text_path):
       os.makedirs(folder_Text_path)

    extracted_content = {
        "slides": []
    }

    ppt = Presentation(Path)
    slide_number = 1

    for slide in ppt.slides:
        slide_data = {
            "slide_number": slide_number,
            "content": []
        }

        index = 1 
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                text = shape.text_frame.text.strip()
                preprocess_text = PreprocessTheText(text,relevance_model)
                if preprocess_text:
                  slide_data["content"].append({
                      "type": "text",
                      "text": text,
                      "position": {
                          "left": shape.left,
                          "top": shape.top,
                          "width": shape.width,
                          "height": shape.height
                      }
                  })
            elif hasattr(shape, "image"):
                
                image_data = shape.image.blob
                image_path = os.path.join(folder_image_path, f"image_{slide_number}_{index}.png")
                with open(image_path, 'wb') as f:
                    f.write(image_data)

                slide_data["content"].append({
                    "type": "image",
                    "placeholder": f"[Image {slide_number}_{index}]",
                    "position": {
                        "left": shape.left,
                        "top": shape.top,
                        "width": shape.width,
                        "height": shape.height
                    },
                    "image_path": image_path
                })
                index += 1
        if len(slide_data["content"])>0:
          extracted_content["slides"].append(slide_data)
        slide_number += 1

    file_name = os.path.join(folder_Text_path,f'Data-{folder_name}.json')
    write_json_to_file(extracted_content,file_name)
    return file_name

relevance_model = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")
file_name = PowerPointExtractor('/content/Lecture 8.pptx',relevance_model)