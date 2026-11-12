class QueryService:
    """Entry point for normalized text, voice, and image searches."""

    def __init__(self, search_service, search_history_repository):
        self.search_service = search_service
        self.search_history_repository = search_history_repository

    def text_query(self, text, filters=None, customer_id=None):
        query = (text or "").strip()
        results = self.search_service.search_text(query, filters)
        if query:
            self.search_history_repository.add(customer_id, "text", query)
        return {"type": "text", "query": query, "results": results}

    def voice_query(self, transcript, filters=None, customer_id=None):
        query = (transcript or "").strip()
        results = self.search_service.search_text(query, filters)
        if query:
            self.search_history_repository.add(
                customer_id, "voice", query, transcript=query
            )
        return {"type": "voice", "query": query, "results": results}

    def image_query(self, image_path, feature_vector, filters=None, customer_id=None):
        results = self.search_service.search_image(feature_vector, filters)
        self.search_history_repository.add(
            customer_id,
            "image",
            "Image search",
            image_path=image_path,
            feature_vector=feature_vector,
        )
        return {"type": "image", "query": "Image search", "results": results}
