class ProductService:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def get_product(self, product_id):
        return self.product_repository.get_product_by_id(product_id)
