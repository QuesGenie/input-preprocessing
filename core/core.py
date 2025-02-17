from pathlib import Path
import re
from typing import List, Union
from nltk.tokenize import word_tokenize

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