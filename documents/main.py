import sys
from utils.preprocessor import InputPreprocessor


def main():
    input_dir = sys.argv[1]
    preprocessor = InputPreprocessor()
    print("Preprocesesing done!")
    chunks, images = preprocessor.process_and_chunk_directory(input_dir)

if __name__ == "__main__":
    main()
    