from data.database import use_connection


class ProductRepository:
    def __init__(self, database):
        self.database = database

    @staticmethod
    def _product(row):
        return dict(row) if row else None

    def all_products(self, connection=None):
        with use_connection(self.database, connection) as conn:
            rows = conn.execute(
                """
                SELECT p.product_id AS id, p.name, p.description, p.price, p.stock,
                       p.image_url AS image, p.color, p.category_id,
                       c.name AS category
                FROM products p JOIN categories c USING (category_id)
                ORDER BY p.product_id
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def get_product_by_id(self, product_id, connection=None):
        with use_connection(self.database, connection) as conn:
            row = conn.execute(
                """
                SELECT p.product_id AS id, p.name, p.description, p.price, p.stock,
                       p.image_url AS image, p.color, p.category_id,
                       c.name AS category
                FROM products p JOIN categories c USING (category_id)
                WHERE p.product_id = ?
                """,
                (product_id,),
            ).fetchone()
            return self._product(row)

    def update_stock(self, product_id, quantity, connection):
        cursor = connection.execute(
            "UPDATE products SET stock = ? WHERE product_id = ? AND stock >= 0",
            (quantity, product_id),
        )
        return cursor.rowcount == 1

    def set_stock(self, product_id, quantity):
        with self.database.connect() as connection:
            cursor = connection.execute(
                "UPDATE products SET stock = ? WHERE product_id = ?",
                (quantity, product_id),
            )
            connection.commit()
            return cursor.rowcount == 1

    def add_product(self, name, description, price, stock, image_url, color, category_id):
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO products
                    (name, description, price, stock, image_url, color, category_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, description, price, stock, image_url, color, category_id),
            )
            connection.commit()
            return cursor.lastrowid
