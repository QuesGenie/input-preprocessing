from bertopic import BERTopic


def generate_candidate_labels(text_data, top_words_per_topic=None):
    try:
        topic_model = BERTopic(n_gram_range=(1, 2), min_topic_size=5)
        topics, _ = topic_model.fit_transform(text_data)
        candidate_labels = set()  
        topic_info = topic_model.get_topic_info()
        for topic_id in topic_info["Topic"]:
            if topic_id != -1: 
                top_words = topic_model.get_topic(topic_id)
                if top_words_per_topic:
                    top_words = top_words[:top_words_per_topic]
                candidate_labels.update([word for word, _ in top_words])
        return list(candidate_labels)  
    except Exception as e:
        print(f"Error generating candidate labels with BERTopic: {e}")
        return ["general topic", "key point"]