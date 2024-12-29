from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sentence_transformers import util
import string
import nltk



class TextPreprocessor:
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()

    @staticmethod
    def preprocess_text(text):
        try:
            text = text.lower().translate(str.maketrans("", "", string.punctuation))
            tokens = word_tokenize(text)
            tokens = [TextPreprocessor.lemmatizer.lemmatize(word) for word in tokens if word not in TextPreprocessor.stop_words and len(word) > 2]
            return " ".join(tokens) if len(tokens) >= 5 else None
        except Exception as e:
            print(f"Error in text preprocessing: {e}")
            return None

    @staticmethod
    def is_relevant_text(text, relevance_model, label_embeddings):
        try:
            text_embedding = relevance_model.encode(text)
            similarities = util.cos_sim(text_embedding, label_embeddings)
            threshold = similarities.mean() + similarities.std()
            return similarities.max() > threshold
        except Exception as e:
            print(f"Error evaluating text relevance: {e}")
            return False