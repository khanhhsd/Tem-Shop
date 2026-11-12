from data.database import use_connection


class CartRepository:
    def __init__(self, database):
        self.database = database

    def get_for_customer(self, customer_id, connection=None):
        with use_connection(self.database, connection) as conn:
            cart = conn.execute(
                "SELECT cart_id, customer_id, created_date FROM carts WHERE customer_id = ?",
                (customer_id,),
            ).fetchone()
            if not cart:
                return {"cart_id": None, "items": [], "total": 0.0}
            items = conn.execute(
                """
                SELECT ci.cart_item_id, ci.product_id, ci.quantity, ci.unit_price,
                       p.name, p.stock, p.image_url AS image, p.color,
                       c.name AS category, ci.quantity * ci.unit_price AS line_total
                FROM cart_items ci
                JOIN products p USING (product_id)
                JOIN categories c USING (category_id)
                WHERE ci.cart_id = ?
                ORDER BY ci.cart_item_id
                """,
                (cart["cart_id"],),
            ).fetchall()
            item_dicts = [dict(item) for item in items]
            return {
                **dict(cart),
                "items": item_dicts,
                "total": round(sum(item["line_total"] for item in item_dicts), 2),
            }

    def add_item(self, customer_id, product_id, quantity, unit_price, connection):
        cart = connection.execute(
            "SELECT cart_id FROM carts WHERE customer_id = ?", (customer_id,)
        ).fetchone()
        if not cart:
            cursor = connection.execute(
                "INSERT INTO carts (customer_id) VALUES (?)", (customer_id,)
            )
            cart_id = cursor.lastrowid
        else:
            cart_id = cart["cart_id"]
        connection.execute(
            """
            INSERT INTO cart_items (cart_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(cart_id, product_id)
            DO UPDATE SET quantity = cart_items.quantity + excluded.quantity,
                          unit_price = excluded.unit_price
            """,
            (cart_id, product_id, quantity, unit_price),
        )

    def update_quantity(self, customer_id, product_id, quantity):
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE cart_items SET quantity = ?
                WHERE product_id = ? AND cart_id = (
                    SELECT cart_id FROM carts WHERE customer_id = ?
                )
                """,
                (quantity, product_id, customer_id),
            )
            connection.commit()
            return cursor.rowcount == 1

    def remove_item(self, customer_id, product_id):
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM cart_items
                WHERE product_id = ? AND cart_id = (
                    SELECT cart_id FROM carts WHERE customer_id = ?
                )
                """,
                (product_id, customer_id),
            )
            connection.commit()
            return cursor.rowcount == 1

    def clear(self, customer_id, connection):
        connection.execute(
            "DELETE FROM cart_items WHERE cart_id = "
            "(SELECT cart_id FROM carts WHERE customer_id = ?)",
            (customer_id,),
        )
