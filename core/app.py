import json
import os
from core import Chunk, Chunker

source_dir = '/home/amna/repos/QuesGenie/datasets/preprocessed/' # sys.argv[1]

def parse_preprocessed_file(file_path):
  """Parses the preprocessed JSON file and extracts text content from pages."""
  with open(file_path, 'r') as f:
        data = json.load(f)
        chunks = []
        for page in data['pages']:
          for content in page['content']:
            if content['type'] == 'text':
              stripped = content['text'].strip()
              if stripped:
                chunks.append(Chunk(file_path, page["page_number"],stripped))
            elif content['type'] == 'image' and 'ocr_text' in content:
                stripped = content['ocr_text'].strip()
                if stripped:
                 chunks.append(Chunk(file_path, page["page_number"],stripped))
        return chunks


chunker = Chunker(min_chunk_tokens=5)

sources = []
for source in os.listdir(source_dir):
    json_file=source_dir+source+"/Text/Data-"+source+".json"
    print(sources)
    sources.append(parse_preprocessed_file(json_file))

for chunk in sources[1]:
  print("SOURCE:\n"+chunk.source+"")

  print("PAGE:\n"+str(chunk.page)+"")
  print("CHUNK:\n"+chunk.text+"\n---------------------")
    
# Try different chunking strategies
# sentence_chunks = chunker.split_by_sentence(source[0])
# print("Semantic chunks:\n")
# for chunk in semantic_chunks:
#   print("CHUNK:\n"+chunk.text+"\n---------------------")
# fixed_chunks = chunker.split_fixed_windows(source[0], window_size=2)
# sliding_chunks = chunker.split_sliding_windows(source[0], window_size=3, overlap=1)