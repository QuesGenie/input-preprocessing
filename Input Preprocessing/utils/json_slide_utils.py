import json

class JsonUtils:
    @staticmethod
    def add_text_to_json_format(text,slide):
        slide["content"].append({
            "type": "text",
            "text": text,
        })

    @staticmethod
    def add_image_to_json_format(slide,image_tuple):
        slide["content"].append({
            "type": "image",
            "placeholder": f"[Image {image_tuple[1]+1}]",
            "image_path": image_tuple[2]
        })
    @staticmethod
    def add_image_text_to_json_format(slide,ocr_text):
        slide["content"].append({
            "type": "image",
            "ocr_text": ocr_text 
        })
                
    @staticmethod
    def write_json_to_file(data, filename):
        try:
            with open(filename, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
                print(f"JSON data has been written to {filename}")
        except Exception as e:
                print(f"An error occurred while writing JSON to file: {e}")