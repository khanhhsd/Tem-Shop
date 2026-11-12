from data.database import use_connection


class OrderRepository:
    def __init__(self, database):
        self.database = database

    def create(self, customer_id, total_amount, connection):
        cursor = connection.execute(
            "INSERT INTO orders (customer_id, total_amount) VALUES (?, ?)",
            (customer_id, total_amount),
        )
        return cursor.lastrowid

    def add_item(self, order_id, product_id, quantity, unit_price, connection):
        connection.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, product_id, quantity, unit_price),
        )

    def create_payment(
        self,
        order_id,
        amount,
        method,
        status,
        connection,
        card_number_masked=None,
        card_holder_name=None,
        received_by=None,
        change_given=None,
    ):
        connection.execute(
            """
            INSERT INTO payments
                (order_id, amount, status, payment_method, card_number_masked,
                 card_holder_name, received_by, change_given)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                amount,
                status,
                method,
                card_number_masked,
                card_holder_name,
                received_by,
                change_given,
            ),
        )

    def create_shipping(self, order_id, address, connection):
        connection.execute(
            """
            INSERT INTO shipping
                (order_id, shipping_address, shipping_method, shipping_cost, estimated_delivery)
            VALUES (?, ?, 'Standard', 0, date('now', '+5 days'))
            """,
            (order_id, address),
        )

    def list_for_customer(self, customer_id):
        with self.database.connect() as connection:
            orders = connection.execute(
                """
                SELECT o.order_id, o.order_date, o.status, o.total_amount,
                       p.payment_method, p.status AS payment_status,
                       s.shipping_address, s.shipping_method, s.estimated_delivery
                FROM orders o
                LEFT JOIN payments p USING (order_id)
                LEFT JOIN shipping s USING (order_id)
                WHERE o.customer_id = ?
                ORDER BY o.order_date DESC, o.order_id DESC
                """,
                (customer_id,),
            ).fetchall()
            result = []
            for order in orders:
                order_data = dict(order)
                order_data["items"] = [
                    dict(item)
                    for item in connection.execute(
                        """
                        SELECT oi.product_id, oi.quantity, oi.unit_price, p.name,
                               oi.quantity * oi.unit_price AS line_total
                        FROM order_items oi JOIN products p USING (product_id)
                        WHERE oi.order_id = ?
                        """,
                        (order_data["order_id"],),
                    )
                ]
                result.append(order_data)
            return result
