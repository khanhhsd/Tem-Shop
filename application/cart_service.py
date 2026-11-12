class CartService:
    def __init__(self, database, product_repository, cart_repository):
        self.database = database
        self.product_repository = product_repository
        self.cart_repository = cart_repository

    def get_cart(self, customer_id):
        return self.cart_repository.get_for_customer(customer_id)

    def add(self, customer_id, product_id, quantity):
        if quantity < 1:
            raise ValueError("Quantity must be at least one.")
        with self.database.transaction() as connection:
            product = self.product_repository.get_product_by_id(product_id, connection)
            if not product:
                raise ValueError("That product is no longer available.")
            cart = self.cart_repository.get_for_customer(customer_id, connection)
            in_cart = next(
                (item["quantity"] for item in cart["items"] if item["product_id"] == product_id),
                0,
            )
            if quantity + in_cart > product["stock"]:
                raise ValueError(f"Only {product['stock']} of this item are in stock.")
            self.cart_repository.add_item(
                customer_id, product_id, quantity, product["price"], connection
            )

    def update(self, customer_id, product_id, quantity):
        if quantity < 1:
            raise ValueError("Quantity must be at least one.")
        product = self.product_repository.get_product_by_id(product_id)
        if not product or quantity > product["stock"]:
            raise ValueError("Requested quantity is not available.")
        if not self.cart_repository.update_quantity(customer_id, product_id, quantity):
            raise ValueError("That item is not in your cart.")

    def remove(self, customer_id, product_id):
        if not self.cart_repository.remove_item(customer_id, product_id):
            raise ValueError("That item is not in your cart.")
