# input-preprocessing/api.py
import os
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from input_preprocessing.documents.powerpoint.powerpoint_preprocessing import PowerPointProcessor
from input_preprocessing.documents.pdf.pdf_preprocessing import PDFProcessor
from input_preprocessing.documents.utils.core import Chunker, ImageSource
from input_preprocessing.audio.app import AudioChunk, Transcriber

class InputPreprocessor:
    def __init__(self, output_dir="data/"):
        self.output_dir = output_dir
        self.json_path = os.path.join(output_dir, "json/")
        self.chunker = Chunker(min_chunk_tokens=100)
        self.audio_sources = []
        # Create necessary directories
        os.makedirs(self.json_path, exist_ok=True)

    def create_processor(self, file_path):
        """Factory method to create the appropriate document processor"""
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.pptx':
            return PowerPointProcessor(file_path, self.json_path)
        elif file_extension == '.pdf':
            return PDFProcessor(file_path, "pymupdf", self.json_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def preprocess_document(self, file_path):
        """Process a single document and return its JSON representation"""
        processor = self.create_processor(file_path)
        json_file = processor.extract_text_and_images()
        return json_file

    def preprocess_directory(self, source_dir, parallel=True, max_workers=None):
        """Process all documents in a directory and return their JSON representations"""
        if not os.path.exists(source_dir):
            raise ValueError(f"Source directory does not exist: {source_dir}")
        audio_paths = []
        doc_paths = []
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file_path)[1].lower()
                print(file_path)
                if ext in ['.pdf', '.pptx']:  # Add more extensions as needed
                    doc_paths.append(file_path)
                elif ext in [".mp3", ".wav", ".audio"]:
                    self.audio_sources.append(file_path)
            print(self.audio_sources)
        # Process files sequentially or in parallel
        if parallel and len(doc_paths) > 1:
            if max_workers is None:
                max_workers = min(multiprocessing.cpu_count(), len(doc_paths))

            results = {}
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks and keep track of them
                future_to_path = {executor.submit(self.preprocess_document, path): path for path in doc_paths}

                # Process results as they complete
                for future in future_to_path:
                    path = future_to_path[future]
                    try:
                        json_file = future.result()
                        results[path] = json_file
                    except Exception as e:
                        print(f"Error processing {path}: {e}")
        else:
            # Sequential processing
            results = {}
            for path in doc_paths:
                try:
                    json_file = self.preprocess_document(path)
                    results[path] = json_file
                except Exception as e:
                    print(f"Error processing {path}: {e}")
        return results

    def chunk_documents(
        self, json_files, strategy="merge", parallel=True, max_workers=None
    ):
        """Chunk multiple processed documents and return all chunks and images"""
        if isinstance(json_files, str):
            # Single JSON file
            return {json_files: self.chunker.chunk(json_files, strategy=strategy)}

        if parallel and len(json_files) > 1:
            if max_workers is None:
                max_workers = min(multiprocessing.cpu_count(), len(json_files))

            results = {}
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_json = {executor.submit(self.chunker.chunk, json_path, strategy): json_path 
                                 for json_path in json_files.values()}

                for future in future_to_json:
                    json_path = future_to_json[future]
                    try:
                        result = future.result()
                        results[json_path] = result
                    except Exception as e:
                        print(f"Error chunking {json_path}: {e}")

            all_chunks = []
            all_images = []
            for result in results.values():
                all_chunks.extend(all_chunks)
                all_images.extend(result[1])

        else:
            # Sequential processing
            all_chunks = []
            all_images = []
            for original_path, json_path in json_files.items():
                chunks, images = self.chunker.chunk(json_path, strategy=strategy)
                all_chunks.extend(chunks)
                all_images.extend(images)
        return all_chunks, all_images

    def chunk_audio(self):
        model = Transcriber('base')
        audio_chunks = []
        for file in self.audio_sources:
            chunks, _ = model.audio_to_sources(file)
            audio_chunks.extend(chunks)
        return audio_chunks

    def process_and_chunk_directory(self, source_dir, chunk_strategy='merge', parallel=True):
        """Complete pipeline: process all documents in a directory and chunk them"""
        json_files = self.preprocess_directory(source_dir, parallel=parallel)
        chunks, images = self.chunk_documents(json_files, strategy=chunk_strategy, parallel=parallel)
        chunks.extend(self.chunk_audio())
        i=1
        for chunk in chunks:
            print(i)
            print(chunk.text)
            i+=1
        return chunks, images
