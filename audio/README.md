# Audio Preprocessing

This module preprocesses audio inputs for transcription using OpenAI's Whisper model.

## 🚀 **Setup and Installation**

### 1. **Install Dependencies**

Make sure Python 3.8+ is installed.

```bash
pip install -r ../requirements.txt
```

### 2. **Download Whisper Model**

Ensure you have Whisper installed:

```bash
pip install git+https://github.com/openai/whisper.git -q
```

## 📚 **Usage**

### 1. **Import the WhisperAudioTranscript Class**

```python
from audio.transcript import WhisperAudioTranscript
```

### 2. **Initialize the Audio Transcript Processor**

```python
import whisper

model = whisper.load_model("base")
audio_processor = WhisperAudioTranscript("path/to/audio.mp3", model)
```

### 3. **Generate Transcript**

```python
transcript = audio_processor.get_transcript()
print(transcript)
```

## 📂 **File Structure**

- `transcript.py`: Contains the `WhisperAudioTranscript` class for audio processing.
