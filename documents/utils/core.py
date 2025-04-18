import json
import os
from pathlib import Path
import re
from typing import List, Union, Optional
from nltk.tokenize import word_tokenize
from langchain_text_splitters import RecursiveCharacterTextSplitter
from input_preprocessing.documents.utils.retriever import Retriever

# Json utilities
def add_text_to_json_format(text,slide):
    slide["content"].append({
        "type": "text",
        "text": text,
    })

def add_image_to_json_format(slide,image_tuple):
    slide["content"].append({
        "type": "image",
        "placeholder": f"[Image {image_tuple[1]+1}]",
        "image_path": image_tuple[2]
    })

def add_image_text_to_json_format(slide,ocr_text):
    slide["content"].append({
        "type": "image",
        "ocr_text": ocr_text 
    })

def write_json_to_file(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
            print(f"JSON data has been written to {filename}")
    except Exception as e:
        print(f"An error occurred while writing JSON to file: {e}")


class Chunk:

    def __init__(self, source: str, type: str, start: int, end: int, text: str):
        self.source = source
        self.type = type
        self.start = start
        self.end = end
        self.text = text
        self._visited = False

    def __str__(self):
        if self.start != self.end:
            range = f"{self.start-self.end}"
        else:
            range = self.start

        if self.type == "ppt":
            return (
                f"Chunk(source={self.source}\nslide={range}\n" f"text={self.text}...)\n"
            )
        else:
            return (
                f"Chunk(source={self.source}\npage={range}\n" f"text={self.text}...)\n"
            )

    @staticmethod
    def merge_chunks(chunk1: 'Chunk', chunk2: 'Chunk') -> 'Chunk':
        """Merge two chunks, handling page ranges appropriately."""
        if chunk1.source != chunk2.source:
            raise ValueError("Cannot merge chunks from different sources")

        merged_start = min(chunk1.start, chunk2.start)
        merged_end = max(chunk1.end, chunk2.end)

        merged_text = f"{chunk1.text} {chunk2.text}".strip()

        return Chunk(
            source=chunk1.source,
            type=chunk1.type,
            start=merged_start,
            end=merged_end,
            text=merged_text,
        )


class Chunker:

    def __init__(self, min_chunk_tokens: int = 200):
        self.min_chunk_tokens = min_chunk_tokens

    @staticmethod
    def _json_to_chunks_and_images(file_path):
        """Parses the preprocessed JSON file and extracts text chunks and images from pages."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            chunks = []
            images = []
            for page in data['pages']:
                for content in page['content']:
                    if content['type'] == 'text':
                        stripped = (
                            content["text"]
                            .strip()
                            .replace("\n", " ")
                            .replace("\t", " ")
                        )
                        if stripped:
                            chunks.append(
                                Chunk(
                                    source=file_path,
                                    type=data["type"],
                                    start=page["page_number"],
                                    end=page["page_number"],
                                    text=stripped,
                                )
                            )
                    elif content['type'] == 'image':
                        if 'ocr_text' in content:
                            stripped = content['ocr_text'].strip()
                            if stripped:
                                chunks.append(
                                    Chunk(
                                        source=file_path,
                                        type=data["type"],
                                        start=page["page_number"],
                                        end=page["page_number"],
                                        text=stripped,
                                    )
                                )
                        if 'image_path' in content:
                            images.append(
                                ImageSource(
                                    source=file_path,
                                    type=data["type"],
                                    loc=page["page_number"],
                                    file_path=content["image_path"],
                                )
                            )
            return chunks, images

    def _chunk_to_lines(self, chunk: Chunk):
        text = chunk.text
        lines = text.splitlines()
        return lines

    def _remove_lines(self, chunk: Chunk, lines_to_remove: List[str]):
        lines = self._chunk_to_lines(chunk)
        filtered_lines = [line for line in lines if line not in lines_to_remove]
        chunk.text = " ".join(filtered_lines)
        return chunk

    def _get_bad_lines(self, lines: List[str], threshold=3):
        line_counts = {}
        for line in lines:
            line = line.strip()
            if line in line_counts:
                line_counts[line] += 1
            else:
                line_counts[line] = 1
        bad_lines = [line for line, count in line_counts.items() if count > threshold]
        return bad_lines

    def _preprocess_chunks(self, chunks: List[Chunk]):
        all_lines = []
        for chunk in chunks:
            all_lines.extend(self._chunk_to_lines(chunk))
        bad_lines = self._get_bad_lines(all_lines)
        for chunk in chunks:
            self._remove_lines(chunk, bad_lines)
        return chunks

    def chunk(self, filename, strategy="merge", rag=True):
        chunks, images = self._json_to_chunks_and_images(filename)
        chunks = self._rechunk(chunks, strategy)
        if rag==True:
            chunks = Retriever(chunks).extract_key_chunks()
        return chunks, images

    def _rechunk(self, chunk_list, strategy='none', **kwargs):
        """
        Higher-order function that returns the appropriate chunking function based on strategy.
        
        Args:
            chunk_list: List of chunks to process
            strategy: Chunking strategy to use ('none', 'sentence', 'fixed', 'sliding', 'merge', 'recursive')
            **kwargs: Additional arguments to pass to the chunking functions
                - window_size: Size of window for fixed and sliding window strategies
                - overlap: Overlap size for sliding window strategy
                - chunk_size: Size of chunks for recursive strategy
                - chunk_overlap: Overlap size for recursive strategy
                - separators: List of separators for recursive strategy
        
        Returns:
            Function that implements the requested chunking strategy
        """
        strategies = {
            'none': lambda chunks: chunks,
            'sentence': lambda chunks: self.split_by_sentence(chunks),
            'fixed': lambda chunks: self.split_fixed_windows(
                chunks, 
                window_size=kwargs.get('window_size', 100)
            ),
            'sliding': lambda chunks: self.split_sliding_windows(
                chunks,
                window_size=kwargs.get('window_size', 100),
                overlap=kwargs.get('overlap', 50)
            ),
            'merge': lambda chunks: self.merge_small_chunks(chunks),
            'recursive': lambda chunks: self.split_recursive(
                chunks,
                chunk_size=kwargs.get('chunk_size', 1000),
                chunk_overlap=kwargs.get('chunk_overlap', 200),
                separators=kwargs.get('separators', None)
            )
        }

        if strategy not in strategies:
            raise ValueError(f"Unknown chunking strategy: {strategy}. "
                        f"Available strategies: {', '.join(strategies.keys())}")

        return strategies[strategy](chunk_list)

    def _validate_chunk(self, chunk: Chunk) -> bool:
        """Validates if a chunk meets the minimum token threshold."""
        tokens = word_tokenize(chunk.text.strip())
        return len(tokens) >= self.min_chunk_tokens

    def split_by_sentence(self, chunks: List[Chunk]) -> List[Chunk]:
        """Split each chunk into sentence-level chunks."""
        result = []
        for chunk in chunks:
            # Simple sentence splitting - could be made more sophisticated
            sentences = re.split(r'(?<=[.!?])\s+', chunk.text)
            for sentence in sentences:
                if sentence.strip():
                    new_chunk = Chunk(
                        chunk.source, chunk.type, chunk.start, chunk.end, sentence
                    )
                    if self._validate_chunk(new_chunk):
                        result.append(new_chunk)
        return result

    def split_fixed_windows(self, chunks: List[Chunk], window_size: int = 100) -> List[Chunk]:
        """Split chunks into fixed-size token windows."""
        result = []
        for chunk in chunks:
            text = word_tokenize(chunk.text.strip())
            for i in range(0, len(text), window_size):
                window = text[i:i + window_size]
                if window:
                    new_chunk = Chunk(
                        chunk.source, chunk.type, chunk.start, chunk.end, window
                    )
                    if self._validate_chunk(new_chunk):
                        result.append(new_chunk)
        return result

    def split_sliding_windows(self, chunks: List[Chunk], window_size: int = 100, overlap: int = 50) -> List[Chunk]:
        """Split chunks into overlapping token windows."""
        if overlap >= window_size:
            raise ValueError("Overlap must be less than window size")

        step = window_size - overlap
        if step <= 0:
            raise ValueError("Step size must be positive")

        result = []
        for chunk in chunks:
            text = word_tokenize(chunk.text.strip())
            for i in range(0, len(text), step):
                window = text[i:i + window_size].strip()
                if window:
                    new_chunk = Chunk(
                        chunk.source, chunk.type, chunk.start, chunk.end, window
                    )
                    if self._validate_chunk(new_chunk):
                        result.append(new_chunk)
        return result

    def merge_small_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Merge consecutive small chunks until they meet the token threshold."""
        if not chunks:
            return []

        result = []
        current = chunks[0]

        for next_chunk in chunks[1:]:
            if self._validate_chunk(current):
                result.append(current)
                current = next_chunk

            merged = Chunk.merge_chunks(current, next_chunk)
            if self._validate_chunk(merged):
                result.append(current)
                current = next_chunk
            else:
                current = merged

        if self._validate_chunk(current):
            result.append(current)

        return result

    def split_recursive(self, 
                    chunks: List[Chunk], 
                    chunk_size: int = 1000, 
                    chunk_overlap: int = 200, 
                    separators: Optional[List[str]] = None) -> List[Chunk]:
        """
        Split chunks using LangChain's recursive text splitter while preserving metadata.
        
        Args:
            chunks: List of Chunk objects to split
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters of overlap between chunks
            separators: Optional list of separators to use for splitting. Defaults to 
                    ["\n\n", "\n", ". ", " ", ""]
        
        Returns:
            List of new Chunk objects with semantic splitting applied
        """
        if not chunks:
            return []

        # Use default separators if none provided
        if separators is None:
            separators = ["\n\n", "\n", ". ", " ", ""]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators
        )

        result = []

        for chunk in chunks:
            # Split the text while preserving the source and page metadata
            split_texts = splitter.split_text(chunk.text)

            # Create new chunks with the split text but same metadata
            for text in split_texts:
                new_chunk = Chunk(
                    source=chunk.source,
                    type=chunk.type,
                    start=chunk.start,
                    end=chunk.end,
                    text=text,
                )
                if self._validate_chunk(new_chunk):
                    result.append(new_chunk)
        return result


class ImageSource(Chunk):
    def __init__(self, source, type, loc, file_path):
        self.source = source
        self.type = type
        self.loc = loc  # page or slide
        self.file_path = file_path

    def __str__(self):
        return f"ImageSource(source={self.source}, loc={self.loc}, file_path={self.file_path})"
