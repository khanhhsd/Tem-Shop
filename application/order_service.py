import re


class OrderService:
    def __init__(
        self,
        database,
        product_repository,
        cart_repository,
        order_repository,
        customer_repository,
    ):
        self.database = database
        self.product_repository = product_repository
        self.cart_repository = cart_repository
        self.order_repository = order_repository
        self.customer_repository = customer_repository

    def list_for_customer(self, customer_id):
        return self.order_repository.list_for_customer(customer_id)

    def checkout(
        self,
        customer_id,
        shipping_address,
        payment_method,
        card_number="",
        card_holder_name="",
        cash_received=0,
    ):
        shipping_address = (shipping_address or "").strip()
        if not shipping_address:
            raise ValueError("A shipping address is required.")
        if payment_method not in {"credit", "cash"}:
            raise ValueError("Choose a supported payment method.")
        digits = re.sub(r"\D", "", card_number or "")
        holder = (card_holder_name or "").strip()
        if payment_method == "credit" and (
            not 13 <= len(digits) <= 19 or not holder
        ):
            raise ValueError("Enter a cardholder name and a valid 13–19 digit card number.")

        with self.database.transaction() as connection:
            cart = self.cart_repository.get_for_customer(customer_id, connection)
            if not cart["items"]:
                raise ValueError("Your cart is empty.")
            for item in cart["items"]:
                product = self.product_repository.get_product_by_id(
                    item["product_id"], connection
                )
                if not product or product["stock"] < item["quantity"]:
                    raise ValueError(
                        f"Not enough stock is available for {item['name']}. Update your cart and try again."
                    )

            total = round(cart["total"], 2)
            customer = self.customer_repository.get_by_id(customer_id, connection)
            change = None
            payment_status = "Paid"
            if payment_method == "cash":
                try:
                    tendered = round(float(cash_received), 2)
                except (TypeError, ValueError) as exc:
                    raise ValueError("Enter the cash amount you will pay.") from exc
                if tendered < total:
                    raise ValueError("Cash received must cover the order total.")
                change = round(tendered - total, 2)
                payment_status = "Pay on delivery"

            order_id = self.order_repository.create(customer_id, total, connection)
            for item in cart["items"]:
                self.order_repository.add_item(
                    order_id,
                    item["product_id"],
                    item["quantity"],
                    item["unit_price"],
                    connection,
                )
                self.product_repository.update_stock(
                    item["product_id"],
                    item["stock"] - item["quantity"],
                    connection,
                )

            masked_number = f"**** **** **** {digits[-4:]}" if digits else None
            self.order_repository.create_payment(
                order_id,
                total,
                payment_method,
                payment_status,
                connection,
                card_number_masked=masked_number,
                card_holder_name=holder or None,
                received_by=customer["name"] if payment_method == "cash" else None,
                change_given=change,
            )
            self.order_repository.create_shipping(order_id, shipping_address, connection)
            self.cart_repository.clear(customer_id, connection)
            return order_id
