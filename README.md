# Input Preprocessing

This module handles preprocessing for both **audio inputs** and **document inputs** in the Question Generation Project.

## 🚀 **Setup and Installation**

### 1. **Clone the Repository**

```bash
git clone <repository-url>
cd input-preprocessing
```

### 2. **Install Dependencies**

Make sure Python 3.8+ is installed.

```bash
pip install -r requirements.txt
```

## 📂 **Structure**

The repository contains the following subfolders:

- **`audio`**: For handling audio input preprocessing.
- **`documents`**: For handling PDF and PowerPoint document preprocessing.

Each folder contains its own README for specific instructions.

```plaintext
input-preprocessing/
|__ app.py
├── audio/
│      ├── samples/
│      ├── app.py 
│      └── README.md
├── documents/
│      ├── pdf/
│      │   └── PdfPreprocessing.py
│      ├── ppt/
│      │   └── PowerPointPreprocessing.py
│      ├── filters/
│      |   ├── extract.py
│      |   └── preprocessing.py
│      ├── utils/
│      |   ├── candidate_labels.py
│      |   └── Json.py
│      └── README.md
├── requirements.txt
└── README.md
```

## 📚 **Usage**

Run the preprocessing scripts from their respective folders:

- For audio: Refer to the `audio/README.md`.
- For documents: Refer to the `document/README.md`.
