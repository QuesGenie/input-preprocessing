from bertopic import BERTopic



class LabelGenerator:
    @staticmethod
    def generate_labels(text_data, relevance_model, top_words_per_topic=5):
        try:
            topic_model = BERTopic(n_gram_range=(1, 2), min_topic_size=5)
            topics, _ = topic_model.fit_transform(text_data)
            candidate_labels = set()

            for topic_id in topic_model.get_topic_info()["Topic"]:
                if topic_id != -1:
                    top_words = topic_model.get_topic(topic_id)[:top_words_per_topic]
                    candidate_labels.update([word for word, _ in top_words])

            return list(candidate_labels)
        except Exception as e:
            print(f"Error generating candidate labels: {e}")
            return ["general topic", "key point"]



