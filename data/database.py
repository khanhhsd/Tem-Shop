import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from werkzeug.security import generate_password_hash


class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def transaction(self):
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                yield connection
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    def initialize(self, catalog_path):
        with self.connect() as connection:
            schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
            connection.executescript(schema)
            categories = [
                (1, "Wear"),
                (2, "Carry"),
                (3, "Home"),
                (4, "Collectibles"),
            ]
            connection.executemany(
                "INSERT OR IGNORE INTO categories (category_id, name) VALUES (?, ?)",
                categories,
            )
            products = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
            category_map = {
                "Shoes": 1,
                "Clothing": 1,
                "Bags": 2,
                "Accessories": 2,
                "Home": 3,
                "Collectibles": 4,
            }
            connection.executemany(
                """
                INSERT INTO products
                    (product_id, name, description, price, stock, image_url, color, category_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(product_id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    price = excluded.price,
                    image_url = excluded.image_url,
                    color = excluded.color,
                    category_id = excluded.category_id
                """,
                [
                    (
                        product["id"],
                        product["name"],
                        product["description"],
                        product["price"],
                        product["stock"],
                        product["image"],
                        product.get("color", ""),
                        category_map[product["category"]],
                    )
                    for product in products
                ],
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO customers
                    (name, email, password_hash, is_admin, customer_type)
                VALUES (?, ?, ?, 1, 'vip')
                """,
                (
                    "Local Admin",
                    "admin@example.com",
                    generate_password_hash("admin1234"),
                ),
            )
            connection.commit()


@contextmanager
def use_connection(database, connection=None):
    if connection is not None:
        yield connection
    else:
        with database.connect() as owned_connection:
            yield owned_connection
