import sys

from powerpoint.powerpoint_preprocessing import *
from pdf.pdf_preprocessing import *

class DocumentProcessorFactory:
    @staticmethod
    def create_processor(file_path: str, output_path) -> DocumentProcessor:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.pptx':
            return PowerPointProcessor(file_path, output_path)
        elif file_extension == '.pdf':
            return PDFProcessor(file_path, 'pymupdf', output_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")


def main():    
    # File path
    file_path = sys.argv[1]

    # Output path
    output_path = sys.argv[2]
    if not output_path:
        output_path='Data'

    if os.path.exists(file_path):
        processor = DocumentProcessorFactory.create_processor(file_path, output_path)
        output_file = processor.extract_text_and_images()
        processor.print_stats()

if __name__ == "__main__":
    main()