from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import string
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


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
        result = relevance_model(text, candidate_labels=labels)
        return max(result["scores"]) > 0.4
    except Exception as e:
        print(f"Error with relevance model: {e}")
        return False
        