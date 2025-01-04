# Document Preprocessing

This module preprocesses PDF and PowerPoint files, extracting text and images for question generation.

## 🚀 **Setup and Installation**

### 1. **Install Dependencies**

Make sure Python 3.8+ is installed.

```bash
pip install -r ../requirements.txt
```

## 📚 **Usage**

### 1. **PDF Processing**

#### Import the `PDFProcessor` Class

```python
from document.pdf_processor import PDFProcessor
```

#### Initialize and Process a PDF

```python
from your_relevance_model import YourRelevanceModel

relevance_model = YourRelevanceModel()
pdf_processor = PDFProcessor("path/to/document.pdf", relevance_model)
output_file = pdf_processor.extract_text_and_images()
print(f"Processed content saved in: {output_file}")
```

### 2. **PowerPoint Processing**

#### Import the `PowerPointProcessor` Class

```python
from document.ppt_processor import PowerPointProcessor
```

#### Initialize and Process a PowerPoint File

```python
ppt_processor = PowerPointProcessor("path/to/presentation.pptx", relevance_model)
output_file = ppt_processor.extract_text_and_images()
print(f"Processed content saved in: {output_file}")
```

## 📂 **File Structure**

- `pdf_processor.py`: Processes PDF documents.
- `ppt_processor.py`: Processes PowerPoint presentations.
- `utils/`: Contains utility functions for text extraction and relevance checks.
