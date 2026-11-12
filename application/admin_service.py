from pathlib import Path
import math


class AdminService:
    def __init__(self, product_repository, category_repository, static_directory):
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.static_directory = Path(static_directory)

    def all_products(self):
        return self.product_repository.all_products()

    def categories(self):
        return self.category_repository.all()

    def image_files(self):
        image_directory = self.static_directory / "products"
        return sorted(path.name for path in image_directory.iterdir() if path.is_file())

    def add_product(self, name, description, price, stock, image_url, color, category_id):
        name = (name or "").strip()
        description = (description or "").strip()
        color = (color or "").strip()
        if not name or not description or not math.isfinite(price) or price < 0 or stock < 0:
            raise ValueError("Enter a name, description, non-negative price, and stock.")
        if not image_url.startswith("products/"):
            raise ValueError("Choose an existing catalog image for the product.")
        if not (self.static_directory / image_url).is_file():
            raise ValueError("The selected catalog image does not exist.")
        if category_id not in {category["category_id"] for category in self.categories()}:
            raise ValueError("Choose a valid product category.")
        return self.product_repository.add_product(
            name, description, price, stock, image_url, color, category_id
        )

    def update_stock(self, product_id, stock):
        if stock < 0:
            raise ValueError("Stock cannot be negative.")
        if not self.product_repository.set_stock(product_id, stock):
            raise ValueError("Product not found.")
