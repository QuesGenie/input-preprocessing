from bertopic import BERTopic


def generate_candidate_labels(text_data):
    try:
        topic_model = BERTopic(n_gram_range=(1, 2), min_topic_size=5, verbose=True)
        topics, _ = topic_model.fit_transform(text_data)
        candidate_labels = []
        topic_info = topic_model.get_topic_info()
        for topic_id in topic_info["Topic"]:
            if topic_id != -1: 
                top_words = topic_model.get_topic(topic_id)
                label = " ".join([word for word, _ in top_words[:3]])  
                candidate_labels.append(label)
        return candidate_labels
    except Exception as e:
        print(f"Error generating candidate labels with BERTopic: {e}")
        return ["general topic", "key point"]