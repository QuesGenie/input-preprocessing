import json
import os
from pathlib import Path
import re
from typing import List, Union, Optional
from nltk.tokenize import word_tokenize
from langchain_text_splitters import RecursiveCharacterTextSplitter

#Json utilities
@staticmethod
def add_text_to_json_format(text,slide):
    slide["content"].append({
        "type": "text",
        "text": text,
    })

@staticmethod
def add_image_to_json_format(slide,image_tuple):
    slide["content"].append({
        "type": "image",
        "placeholder": f"[Image {image_tuple[1]+1}]",
        "image_path": image_tuple[2]
    })
@staticmethod
def add_image_text_to_json_format(slide,ocr_text):
    slide["content"].append({
        "type": "image",
        "ocr_text": ocr_text 
    })
            
@staticmethod
def write_json_to_file(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
            print(f"JSON data has been written to {filename}")
    except Exception as e:
            print(f"An error occurred while writing JSON to file: {e}")


class PageRange:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end
    
    def __str__(self):
        return f"{self.start}-{self.end}" if self.start != self.end else str(self.start)
    
    @staticmethod
    def from_page(page: Union[int, 'PageRange']) -> 'PageRange':
        """Convert a page number or PageRange to PageRange."""
        if isinstance(page, PageRange):
            return page
        return PageRange(page, page)
    
    @staticmethod
    def merge(page1: Union[int, 'PageRange'], page2: Union[int, 'PageRange']) -> 'PageRange':
        """Merge two page references into a single PageRange."""
        if page1 == page2:
            return page1
        p1 = PageRange.from_page(page1)
        p2 = PageRange.from_page(page2)
        return PageRange(min(p1.start, p2.start), max(p1.end, p2.end))

class Chunk:
    def __init__(self, source: str, page: Union[int, PageRange], text: str):
        self.source = source
        self.page = page
        self.text = text
    
    @staticmethod
    def merge_chunks(chunk1: 'Chunk', chunk2: 'Chunk') -> 'Chunk':
        """Merge two chunks, handling page ranges appropriately."""
        if chunk1.source != chunk2.source:
            raise ValueError("Cannot merge chunks from different sources")
        
        merged_page = PageRange.merge(chunk1.page, chunk2.page)
        merged_text = f"{chunk1.text} {chunk2.text}".strip()
        
        return Chunk(
            source=chunk1.source,
            page=merged_page,
            text=merged_text
        )

class Chunker:
    def __init__(self, min_chunk_tokens: int = 5):
        self.min_chunk_tokens = min_chunk_tokens

    @staticmethod
    def _json_to_chunks(file_path):
        """Parses the preprocessed JSON file and extracts text content from pages."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            chunks = []
            for page in data['pages']:
                for content in page['content']:
                    if content['type'] == 'text':
                        stripped = content['text'].strip()
                        if stripped:
                            chunks.append(Chunk(file_path, page["page_number"], stripped))
                    elif content['type'] == 'image' and 'ocr_text' in content:
                        stripped = content['ocr_text'].strip()
                        if stripped:
                            chunks.append(Chunk(file_path, page["page_number"], stripped))
            return chunks

    def chunk(self, filename, strategy='none'):
        chunks = self._json_to_chunks(filename)
        chunks = self._rechunk(chunks, strategy)
        return chunks
    
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
                    new_chunk = Chunk(chunk.source, chunk.page, sentence)
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
                    page_range = PageRange.from_page(chunk.page)
                    new_chunk = Chunk(chunk.source, page_range, window)
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
                    page_range = PageRange.from_page(chunk.page)
                    new_chunk = Chunk(chunk.source, page_range, window)
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
            if current.source != next_chunk.source:
                if self._validate_chunk(current):
                    result.append(current)
                current = next_chunk
                continue
            
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
                    page=chunk.page,
                    text=text
                )
                if self._validate_chunk(new_chunk):
                    result.append(new_chunk)
        print(result)
        return result
