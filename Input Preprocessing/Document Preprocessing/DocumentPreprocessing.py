from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
import os
import uuid
import time
import json
from typing import Dict, Any


class DocumentProcessor(ABC):
    def __init__(self, path: str, relevance_model: Any):
        self.path = path
        self.relevance_model = relevance_model
        self.folder_name = f"{os.path.splitext(os.path.basename(path))[0]}_{str(uuid.uuid4())}"
        self.folder_path = os.path.join('Data', self.folder_name)
        self.folder_image_path = os.path.join(self.folder_path, 'Images')
        self.folder_text_path = os.path.join(self.folder_path, 'Text')
        self.stats = self._init_stats()
        
        os.makedirs(self.folder_image_path, exist_ok=True)
        os.makedirs(self.folder_text_path, exist_ok=True)

    def _init_stats(self) -> Dict[str, int]:
        return {
            "total_pages": 0,
            "total_images_extracted": 0,
            "total_relevant_text_blocks": 0,
            "total_ocr_text_blocks": 0,
            "processing_time": 0,
        }

    @abstractmethod
    def extract_text_and_images(self) -> str:
        pass

    def write_json_to_file(self, data: Dict, filename: str) -> None:
        try:
            with open(filename, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing JSON to file: {e}")

    def print_stats(self) -> None:
        print(f"\n=== {self.__class__.__name__} Processing Stats ===")
        for key, value in self.stats.items():
            print(f"{key.replace('_', ' ').capitalize()}: {value}")