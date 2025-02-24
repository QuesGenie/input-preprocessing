import sys
from utils.preprocessor import InputPreprocessor

def print_chunks(chunks):
    for chunk in chunks:
            print()
            print("Page: "+str(chunk.page)+" in source: " +chunk.source)
            print("Chunk:\n"+chunk.text+"\n---------------------")
def main():
    input_dir = sys.argv[1]
    preprocessor = InputPreprocessor()
    print("Preprocesesing done!")
    chunks = preprocessor.process_and_chunk_directory(input_dir)['all_chunks']
    print_chunks(chunks)

if __name__ == "__main__":
    main()
    