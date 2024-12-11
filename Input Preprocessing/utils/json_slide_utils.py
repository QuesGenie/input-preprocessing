import json

class JsonUtils:
    @staticmethod
    def add_text_to_json_format(text,slide):
        if text:
            slide["content"].append({
                "type": "text",
                "text": text,
                "position": {"left": 0, "top": 0}
            })

    @staticmethod
    def add_image_to_json_format(slide,image_tuple):
        if image_tuple[0]:
            slide["content"].append({
                    "type": "image",
                    "placeholder": f"[Image {image_tuple[1]+1}]",
                    "position": {"left": image_tuple[0]["x0"], "top": image_tuple[0]["top"]},
                    "image_path": image_tuple[2]
                })
                
    @staticmethod
    def write_json_to_file(data, filename):
        try:
            with open(filename, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
                print(f"JSON data has been written to {filename}")
        except Exception as e:
                print(f"An error occurred while writing JSON to file: {e}")