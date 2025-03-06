from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class Retriever:
    def __init__(self, chunks):
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.tf_idf = TfidfVectorizer(stop_words="english")
        self.chunks=chunks
        
        self.chunk_embeddings = None
        self.tf_idf_matrix = None
        self.key_topics = None

    def _embed_chunks(self):
        texts = [chunk.text for chunk in self.chunks]
        self.chunk_embeddings = self.encoder.encode(texts)

        # Also create TF-IDF representation for topic extraction
        self.tf_idf_matrix = self.tf_idf.fit_transform(texts)

    def _extract_key_topics(self, num_terms=10):
        if not self.chunks:
            return []
        feature_names = self.tf_idf.get_feature_names_out()
        tf_idf_sum = np.array(self.tf_idf_matrix.sum(axis=0))[0]
        top_indices = tf_idf_sum.argsort()[-num_terms:][::-1]
        top_terms = [feature_names[i] for i in top_indices]
        self.key_topics = top_terms

    def _retrieve_relevant_chunks(self, query, top_k=5):
        if not self.chunks or self.chunk_embeddings is None:
            return []

        query_embedding = self.encoder.encode(query)
        similarities = np.dot(self.chunk_embeddings, query_embedding)
        unvisited_similarities = [(i, similarities[i]) 
                                for i in range(len(self.chunks)) 
                                if not self.chunks[i]._visited]

        if len(unvisited_similarities) == 0:
            return []
        top_unvisited = sorted(unvisited_similarities, key=lambda x: x[1], reverse=True)[:top_k]
        
        # Extract the relevant chunks and mark them as visited
        result_chunks = []
        for idx, _ in top_unvisited:
            chunk = self.chunks[idx]
            chunk._visited = True
            result_chunks.append(chunk)
        
        return result_chunks

    def extract_key_chunks(self):
        self._embed_chunks()
        self._extract_key_topics()
        print(f"Key topics:\n{self.key_topics}")
        key_chunks = []
        for topic in self.key_topics:
            key_chunks.extend(self._retrieve_relevant_chunks(topic))
        print(f"Total number of chunks = {len(self.chunks)}")
        print(f"Number of relevant chunks = {len(key_chunks)}")
        self._print_irrelevant_chunks()
        return key_chunks

    def _print_irrelevant_chunks(self):
        irrelevant_chunks = [chunk for chunk in self.chunks if not chunk._visited]
        print("Irrelevant chunks that have been excluded:")
        for chunk in irrelevant_chunks:
            print(chunk)
