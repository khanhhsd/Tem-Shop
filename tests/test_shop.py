import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from main import create_app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ShopApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "shop-test.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-key",
                "DATABASE": str(self.database_path),
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        try:
            for record in self.query("SELECT image_path FROM image_search_queries"):
                image_path = (PROJECT_ROOT / "static" / record["image_path"]).resolve()
                upload_directory = (PROJECT_ROOT / "static" / "uploads").resolve()
                if image_path.parent == upload_directory:
                    image_path.unlink(missing_ok=True)
        finally:
            self.temporary_directory.cleanup()

    def register_customer(self, email="shopper@example.com"):
        return self.client.post(
            "/register",
            data={
                "name": "Test Shopper",
                "email": email,
                "password": "password123",
                "phone": "555-0100",
                "address": "10 Market Street",
            },
            follow_redirects=True,
        )

    def login_admin(self):
        return self.client.post(
            "/login",
            data={"email": "admin@example.com", "password": "admin1234"},
            follow_redirects=True,
        )

    def query(self, statement, params=()):
        connection = sqlite3.connect(self.database_path)
        try:
            connection.row_factory = sqlite3.Row
            return connection.execute(statement, params).fetchall()
        finally:
            connection.close()

    def test_seed_schema_and_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.query("SELECT * FROM products")), 23)
        self.assertEqual(len(self.query("SELECT * FROM categories")), 4)
        self.assertIn(b"Cloudstride Running Shoe", response.data)
        self.assertIn(b"Moonlight Greatsword Display Replica", response.data)
        self.assertIn(b"$50.00", response.data)
        self.assertLess(
            response.data.index(b"Natural Canvas Market Tote"),
            response.data.index(b"Midnight Animatronic Figure"),
        )
        self.assertLess(
            response.data.index(b"Midnight Animatronic Figure"),
            response.data.index(b"Grand Theft Auto VI Collector Poster"),
        )
        self.assertLess(
            response.data.index(b"Grand Theft Auto VI Collector Poster"),
            response.data.index(b"Moonlight Greatsword Display Replica"),
        )

    def test_extra_items_stay_last_in_relevance_results(self):
        search_service = self.app.extensions["shop_services"]["search"]
        results = search_service.search_text("a")
        product_ids = [product["id"] for product, _score in results]
        extra_ids = [product_id for product_id in product_ids if product_id > 20]
        self.assertTrue(extra_ids)
        self.assertEqual(product_ids[-3:], [21, 22, 23])

    def test_seed_catalog_refreshes_prices_without_resetting_stock(self):
        repository = self.app.extensions["shop_services"]["catalog"].product_repository
        database = repository.database
        catalog = json.loads(
            (PROJECT_ROOT / "data" / "products.json").read_text(encoding="utf-8")
        )
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                "UPDATE products SET price = ?, stock = ? WHERE product_id = 21",
                (1.0, 3),
            )
            connection.commit()
        finally:
            connection.close()

        with tempfile.TemporaryDirectory() as directory:
            changed_catalog_path = Path(directory) / "products.json"
            catalog[20]["price"] = 52.75
            catalog[20]["stock"] = 99
            changed_catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            database.initialize(changed_catalog_path)

        updated = self.query(
            "SELECT price, stock FROM products WHERE product_id = 21"
        )[0]
        self.assertEqual(updated["price"], 52.75)
        self.assertEqual(updated["stock"], 3)

    def test_registration_hashes_password_and_login_works(self):
        response = self.register_customer()
        self.assertEqual(response.status_code, 200)
        customer = self.query(
            "SELECT password_hash FROM customers WHERE email = ?",
            ("shopper@example.com",),
        )[0]
        self.assertNotEqual(customer["password_hash"], "password123")
        self.assertTrue(customer["password_hash"].startswith("scrypt:"))
        self.assertIn(b"Your account is ready", response.data)

        self.client.post("/logout")
        login = self.client.post(
            "/login",
            data={"email": "shopper@example.com", "password": "password123"},
        )
        self.assertEqual(login.status_code, 302)

    def test_keyword_search_and_category_filter(self):
        response = self.client.get("/?q=black&category=2")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Large Black Umbrella", response.data)
        self.assertNotIn(b"Black Digital Alarm Clock", response.data)
        self.assertIn(b"View product", response.data)
        self.assertNotIn(b"Add to cart", response.data)

    def test_product_detail_contains_cart_action_and_listing_does_not(self):
        self.register_customer()
        listing = self.client.get("/")
        detail = self.client.get("/products/1")
        self.assertEqual(detail.status_code, 200)
        self.assertIn(b"Add to cart", detail.data)
        self.assertIn(b"Cloudstride Running Shoe", detail.data)
        self.assertNotIn(b"Add to cart", listing.data)
        self.assertEqual(self.client.get("/products/9999").status_code, 404)

    def test_add_to_cart_redirects_to_product_page(self):
        self.register_customer()
        response = self.client.post("/cart/add/1", data={"quantity": "1"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/products/1")

    def test_voice_query_is_saved_with_transcript(self):
        self.register_customer()
        response = self.client.get("/?q=brown+wallet&mode=voice")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Brown Leather Wallet", response.data)
        rows = self.query(
            """
            SELECT s.query_type, v.transcript
            FROM search_histories s JOIN voice_search_queries v USING (search_history_id)
            """
        )
        self.assertEqual((rows[0]["query_type"], rows[0]["transcript"]), ("voice", "brown wallet"))

    def test_image_upload_ranks_catalog_and_records_features(self):
        self.register_customer()
        product_image = PROJECT_ROOT / "static" / "products" / "cloudstride-running-shoe.jpg"
        with product_image.open("rb") as image_file:
            response = self.client.post(
                "/search/image",
                data={"image": (io.BytesIO(image_file.read()), "reference.jpg")},
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Visual matches", response.data)
        saved = self.query(
            """
            SELECT i.image_path, i.feature_vector
            FROM image_search_queries i
            """
        )[0]
        self.assertTrue((PROJECT_ROOT / "static" / saved["image_path"]).is_file())
        self.assertEqual(len(json.loads(saved["feature_vector"])), 12)

    def test_credit_checkout_decrements_stock_and_masks_card(self):
        self.register_customer()
        self.client.post("/cart/add/1", data={"quantity": "2"})
        response = self.client.post(
            "/checkout",
            data={
                "shipping_address": "10 Market Street",
                "payment_method": "credit",
                "card_number": "4111111111111111",
                "card_holder_name": "Test Shopper",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your orders", response.data)
        order = self.query("SELECT order_id, total_amount FROM orders")[0]
        self.assertAlmostEqual(order["total_amount"], 178.00)
        product = self.query("SELECT stock FROM products WHERE product_id = 1")[0]
        self.assertEqual(product["stock"], 16)
        payment = self.query(
            "SELECT card_number_masked, card_holder_name FROM payments"
        )[0]
        self.assertEqual(payment["card_number_masked"], "**** **** **** 1111")
        self.assertNotIn("4111111111111111", payment["card_number_masked"])
        self.assertEqual(len(self.query("SELECT * FROM shipping")), 1)
        self.assertEqual(len(self.query("SELECT * FROM cart_items")), 0)

    def test_failed_checkout_keeps_cart_and_does_not_create_order(self):
        self.register_customer()
        self.client.post("/cart/add/1", data={"quantity": "1"})
        response = self.client.post(
            "/checkout",
            data={
                "shipping_address": "10 Market Street",
                "payment_method": "cash",
                "cash_received": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Cash received must cover the order total", response.data)
        self.assertEqual(len(self.query("SELECT * FROM orders")), 0)
        self.assertEqual(len(self.query("SELECT * FROM cart_items")), 1)

    def test_admin_can_add_product_and_update_stock(self):
        self.login_admin()
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 200)
        self.client.post(
            "/admin/products",
            data={
                "name": "Test Ceramic Bowl",
                "description": "A sturdy serving bowl.",
                "category_id": "3",
                "color": "Cream",
                "price": "25.50",
                "stock": "7",
                "image_file": "ceramic-plant-pot.jpg",
            },
        )
        product = self.query(
            "SELECT product_id FROM products WHERE name = ?", ("Test Ceramic Bowl",)
        )[0]
        self.client.post(
            f"/admin/stock/{product['product_id']}", data={"stock": "13"}
        )
        stock = self.query(
            "SELECT stock FROM products WHERE product_id = ?",
            (product["product_id"],),
        )[0]["stock"]
        self.assertEqual(stock, 13)

    def test_cart_and_orders_require_login(self):
        self.assertEqual(self.client.get("/cart").status_code, 302)
        self.assertEqual(self.client.get("/orders").status_code, 302)


if __name__ == "__main__":
    unittest.main()
