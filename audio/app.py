import whisper
from tqdm import tqdm
    
class AudioChunk:
    def __init__(self, source, start_time, end_time, text):
        self.source = source
        self.start_time = start_time
        self.end_time = end_time
        self.text = text

    def __str__(self):
        return f"AudioChunk(source={self.source}, timestamp={self.start_time}:{self.end_time}, text={self.text})"
    
class Transcriber:
  def __init__(self, model='base'):
    self.model = whisper.load_model(model)

  def _merge_audio_chunks(self, chunks, threshold=200):
    merged_chunks = []
    current_chunk = None

    for chunk in tqdm(chunks):
        if current_chunk is None:
            current_chunk = chunk
        else:
            # Merge the current chunk with the next chunk
            current_chunk.end_time = chunk.end_time
            current_chunk.text += f" {chunk.text}"

            # Check if the merged text ends with a full stop
            if current_chunk.text.endswith('.'):
                # If the merged text is shorter than the threshold, continue merging
                if len(current_chunk.text) < threshold:
                    continue
                else:
                    # Otherwise, finalize the current chunk and start a new one
                    merged_chunks.append(current_chunk)
                    current_chunk = None
    # Append the last chunk if it exists
    if current_chunk:
        merged_chunks.append(current_chunk)
    return merged_chunks

  def audio_to_sources(self, file_path):
    transcript = self.model.transcribe(file_path)
    audio_chunks = [] 
    for segment in transcript['segments']:
        audio_chunks.append(AudioChunk(
            source=file_path,
            start_time=segment['start'],
            end_time=segment['end'],
            text=segment['text']
        ))
    merged_chunks = self._merge_audio_chunks(audio_chunks)
    print(f"Number of original segments: {len(transcript['segments'])}")
    print(f"Number of merged chunks: {len(merged_chunks)}")
    return merged_chunks, transcript['text']

if __name__ == "__main__":
    model = Transcriber('base')
    audio_chunks, transcript = model.audio_to_sources('samples/audio.mp3')
    print("Full transcript:\n" + transcript)
    print("Audio chunks:\n")
    for chunk in audio_chunks:
        print(chunk)
