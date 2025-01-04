from powerpoint.powerpoint_preprocessing import *
from pdf.pdf_preprocessing import *

class DocumentProcessorFactory:
    @staticmethod
    def create_processor(file_path: str, relevance_model: Any) -> DocumentProcessor:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.pptx':
            return PowerPointProcessor(file_path, relevance_model)
        elif file_extension == '.pdf':
            return PDFProcessor(file_path, relevance_model)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")


def main():
    relevance_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Process a PowerPoint file
    ppt_path = './lec.pptx'
    if os.path.exists(ppt_path):
        processor = DocumentProcessorFactory.create_processor(ppt_path, relevance_model)
        output_file = processor.extract_text_and_images()
        processor.print_stats()
    
    # Process a PDF file
    pdf_path = './lec.pdf'
    if os.path.exists(pdf_path):
        processor = DocumentProcessorFactory.create_processor(pdf_path, relevance_model)
        output_file = processor.extract_text_and_images()
        processor.print_stats()

if __name__ == "__main__":
    main()