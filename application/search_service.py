class SearchService:
    def __init__(
        self, product_repository, ranking_service, vector_index, category_repository
    ):
        self.product_repository = product_repository
        self.ranking_service = ranking_service
        self.vector_index = vector_index
        self.category_repository = category_repository

    @staticmethod
    def _filter(products, filters):
        filters = filters or {}
        category_id = filters.get("category_id")
        minimum = filters.get("min_price")
        maximum = filters.get("max_price")
        available_only = filters.get("in_stock", False)
        return [
            product
            for product in products
            if (not category_id or product["category_id"] == category_id)
            and (minimum is None or product["price"] >= minimum)
            and (maximum is None or product["price"] <= maximum)
            and (not available_only or product["stock"] > 0)
        ]

    def search_text(self, query, filters=None):
        products = self._filter(self.product_repository.all_products(), filters)
        return self.ranking_service.rank_text(products, query)

    def browse(self, filters=None):
        return [
            (product, None)
            for product in self._filter(self.product_repository.all_products(), filters)
        ]

    def categories(self):
        return self.category_repository.all()

    def search_image(self, image_vector, filters=None):
        products = self._filter(self.product_repository.all_products(), filters)
        ranked = [
            (
                product,
                self.ranking_service.cosine_similarity(
                    image_vector, self.vector_index.product_vector(product["image"])
                ),
            )
            for product in products
        ]
        return sorted(
            ranked,
            key=lambda match: (match[0]["id"] > 20, -match[1], match[0]["id"]),
        )
