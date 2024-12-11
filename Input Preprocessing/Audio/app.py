import whisper

class WhisperAudioTranscript:
  def __init__(self, audio, model):
    self.audio = whisper.load_audio(audio)
    self.sample_rate = whisper.audio.SAMPLE_RATE
    self.chunk_size = self.sample_rate * 20
    self.model = model
    self.transcription = []
    self.chunks = []

  def chunking(self):
      self.chunks = [self.audio[i:i + self.chunk_size] for i in range(0, len(self.audio), self.chunk_size)]
      return self.chunks

  
  def transcribe(self):
      chunks = self.chunking()

      for idx, chunk in enumerate(self.chunks):
        chunk = whisper.pad_or_trim(chunk)
        mel = whisper.log_mel_spectrogram(chunk).to(self.model.device)
        options = whisper.DecodingOptions()
        result = whisper.decode(model, mel, options)
        self.transcription.append(result.text)

  def get_transcript(self):
    self.transcribe()
    return "".join(self.transcription)

if __name__ === "__main__":
    WhisperBaseModel = whisper.load_model("base")
    audioModel = WhisperAudioTranscript('./samples/audio.mp3',WhisperBaseModel)
    print(audioModel.get_transcript())
