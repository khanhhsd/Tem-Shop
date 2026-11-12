class SearchHistoryService:
    def __init__(self, search_history_repository):
        self.search_history_repository = search_history_repository

    def recent_for_customer(self, customer_id, limit=10):
        return self.search_history_repository.recent_for_customer(customer_id, limit)
