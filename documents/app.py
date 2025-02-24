import sys

from powerpoint.powerpoint_preprocessing import *
from pdf.pdf_preprocessing import *
import utils
import DocumentPreprocessing

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
    source_dir = '/home/amna/repos/QuesGenie/datasets/sources/' # sys.argv[1]

    # Output path
    output_path = 'data/' # sys.argv[0]


    # Doc to json
    json_path = output_path + 'json/'

    for source_path in os.listdir(source_dir):
        print("SOURCE:" + source_path)
        processor = create_processor(source_dir + source_path, json_path)
        json_file = processor.extract_text_and_images()
        source_output=os.path.splitext(os.path.basename(source_path))[0]

    print("Done, sources saved at " + json_path)
    # # Json to chunks
    # for json_dir in os.listdir(json_path):
    #     json_path=json_dir+"/text/data-"+source+".json"
    #     chunked_sources = Chunker(min_chunk_tokens=5).chunk_sources(json_path,strategy='none')
    #     for chunk in chunked_sources[0]:
    #         print("SOURCE:\n"+chunk.source+"")

    #         print("PAGE:\n"+str(chunk.page)+"")
    #         print("CHUNK:\n"+chunk.text+"\n---------------------")
                
if __name__ == "__main__":
    main()