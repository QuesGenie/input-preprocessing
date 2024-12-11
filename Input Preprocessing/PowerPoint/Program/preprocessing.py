from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sentence_transformers import util
import string
import nltk



stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

DOWNLOAD_PACKAGES = False

if DOWNLOAD_PACKAGES:
    nltk.download('stopwords')
    nltk.download('punkt_tab')
    nltk.download('wordnet')


def preprocess_text(text):
    try:
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        tokens = word_tokenize(text)
        tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and len(word) > 2]

        if len(tokens) < 5:
            return None
        return " ".join(tokens)
    except Exception as e:
        print(f"Error in text preprocessing: {e}")
        return None


def is_relevant_text(text, relevance_model,labels):
    try:

        # result = relevance_model(text, candidate_labels=labels)
        # return max(result["scores"]) > 0.3
        text_embedding = relevance_model.encode(text)
        score = util.cos_sim(text_embedding, labels).max()
        return score > 0.3  # Adjust threshold as needed
    except Exception as e:
        print(f"Error with relevance model: {e}")
        return False