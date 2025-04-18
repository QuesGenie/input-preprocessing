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
        self.chunker = Chunker(min_chunk_tokens=5)
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

    def _chunk_to_lines(self, chunk: Chunk):
        text = chunk.text
        lines = text.splitlines()
        return lines

    def _remove_lines(self, chunk: Chunk, lines_to_remove: List[str]):
        lines = self._chunk_to_lines(chunk)
        filtered_lines = [line for line in lines if line not in lines_to_remove]
        chunk.text = " ".join(filtered_lines)
        return chunk

    def _get_frequent_lines(self, lines: List[str], threshold=3):
        line_counts = {}
        for line in lines:
            line = line.strip()
            if line in line_counts:
                line_counts[line] += 1
            else:
                line_counts[line] = 1
        for line in line_counts:
            print(f"{line_counts[line]}- {line}")
        frequent_lines = [
            line for line, count in line_counts.items() if count > threshold
        ]
        # debugging
        frequent_lines.sort(key=lambda x: line_counts[x], reverse=True)
        for line in frequent_lines:
            print(f"{line}")
        # debugging end
        return frequent_lines

    def _preprocess_chunks(self, chunks: List[Chunk]):
        all_lines = []
        for chunk in chunks:
            all_lines.extend(self._chunk_to_lines(chunk))
        frequent_lines = self._get_frequent_lines(all_lines)
        for chunk in chunks:
            print("BEFORE")
            print(chunk.text)
            self._remove_lines(chunk, frequent_lines)
            print("AFTER")
            print(chunk.text)
        return chunks

    def chunk_documents(self, json_files, strategy='none', parallel=True, max_workers=None):
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
                clean_chunks = self._preprocess_chunks(result[0])

                all_chunks.extend(clean_chunks)
                all_images.extend(result[1])

        else:
            # Sequential processing
            all_chunks = []
            all_images = []
            for original_path, json_path in json_files.items():
                chunks, images = self.chunker.chunk(json_path, strategy=strategy)
                clean_chunks = self._preprocess_chunks(chunks)

                all_chunks.extend(clean_chunks)
                all_images.extend(images)
        return clean_chunks, all_images

    def chunk_audio(self):
        model = Transcriber('base')
        audio_chunks = []
        for file in self.audio_sources:
            chunks, _ = model.audio_to_sources(file)
            audio_chunks.extend(chunks)
        return audio_chunks

    def process_and_chunk_directory(self, source_dir, chunk_strategy='none', parallel=True):
        """Complete pipeline: process all documents in a directory and chunk them"""
        json_files = self.preprocess_directory(source_dir, parallel=parallel)
        chunks, images = self.chunk_documents(json_files, strategy=chunk_strategy, parallel=parallel)
        chunks.extend(self.chunk_audio())
        return chunks, images
