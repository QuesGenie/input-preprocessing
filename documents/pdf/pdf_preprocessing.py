from tqdm.auto import tqdm
import shutil
from DocumentPreprocessing import *
from filters.extract import *
from pdf.pdf_plumber import *
from pdf.py_mupdf import *




class PDFProcessor(DocumentProcessor):
    def __init__(self, path: str, pdf_engine, output_path):
        super().__init__(path, output_path)
        self.pdf_engine = self._get_pdf_engine(pdf_engine)

    def _get_pdf_engine(self, engine_name: str):
        engines = {
            'pymupdf': Pymupdf(),
            'pdfplumber': PDFPlumber()
        }
        return engines.get(engine_name.lower(),Pymupdf())

    def extract_text_and_images(self,file_name=None) -> str:
        if file_name==None:
            filename = os.path.join(self.folder_text_path, f"{self.folder_name}.json")

        try:
            start_time = time.time()
            
            # Get raw content using the selected PDF engine
            raw_content = self.pdf_engine.extract_text_and_images(
                self.path, self.folder_image_path
            )

            processed_content=self._process_content(raw_content)

            self.write_json_to_file(processed_content, filename)
            
            self.stats["processing_time"] = time.time() - start_time
            return filename

        except Exception as e:
            print(f"Error processing PDF: {e}")
            shutil.rmtree(self.folder_path, ignore_errors=True)
            return ""

    def _collect_all_text(self, content: Dict) -> list:
        texts = []
        for page in content.get("pages", []):
            for item in page.get("content", []):
                if item.get("type") == "text":
                    texts.append(item.get("text"))
        return texts

    def _process_content(self, content: Dict) -> Dict:
        processed_content = {"pages": []}
        
        for slide in content.get("pages", []):
            processed_slide = self._process_slide(slide)
            if processed_slide["content"]:
                processed_content["pages"].append(processed_slide)
            self.stats["total_pages"] += 1

        return processed_content

    def _process_slide(self, slide: Dict) -> Dict:
        processed_slide = {"page_number": slide["page_number"], "content": []}
        
        for item in slide.get("content", []):
            if item.get("type") == "text":
                self._process_text_item(item, processed_slide)
            elif item.get("type") == "image":
                self._process_image_item(item, processed_slide)
                
        return processed_slide

    def _process_text_item(self, item: Dict, processed_slide: Dict) -> None:
        text = item.get("text", "")
        if text:
            processed_slide["content"].append({
                "type": "text",
                "text": text
            })
            self.stats["total_text_blocks"] += 1

    def _process_image_item(self, item: Dict, processed_slide: Dict) -> None:
        image_path = item.get("image_path")
        if image_path:
            with open(image_path, "rb") as img_file:
                image_blob = img_file.read()
            ocr_text = TextExtractor.extract_text_from_image(image_blob)
            if ocr_text:
                processed_slide["content"].append({
                    "type": "image",
                    "image_path": image_path,
                    "ocr_text": ocr_text
                })
                self.stats["total_ocr_text_blocks"] += 1
            else:
                processed_slide["content"].append({
                    "type": "image",
                    "image_path": image_path
                })
                self.stats["total_images_extracted"] += 1