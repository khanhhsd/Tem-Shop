import os
from pathlib import Path

from flask import Flask
from werkzeug.exceptions import RequestEntityTooLarge

from application.admin_service import AdminService
from application.auth_service import AuthService
from application.cart_service import CartService
from application.file_storage import FileStorage
from application.image_service import ImageService
from application.order_service import OrderService
from application.product_service import ProductService
from application.query_service import QueryService
from application.ranking_service import RankingService
from application.search_service import SearchService
from application.search_history_service import SearchHistoryService
from application.speech_service import SpeechService
from application.vector_index import VectorIndex
from controllers.admin_controller import register_routes as register_admin_routes
from controllers.auth_controller import register_routes as register_auth_routes
from controllers.cart_controller import register_routes as register_cart_routes
from controllers.catalog_controller import register_routes as register_catalog_routes
from controllers.helpers import current_customer
from controllers.order_controller import register_routes as register_order_routes
from data.cart_repository import CartRepository
from data.category_repository import CategoryRepository
from data.customer_repository import CustomerRepository
from data.database import Database
from data.order_repository import OrderRepository
from data.product_repository import ProductRepository
from data.search_history_repository import SearchHistoryRepository


PROJECT_ROOT = Path(__file__).resolve().parent


def register_controllers(app):
    register_catalog_routes(app)
    register_auth_routes(app)
    register_cart_routes(app)
    register_order_routes(app)
    register_admin_routes(app)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "local-development-secret-change-me"),
        DATABASE=os.path.join(app.instance_path, "shop.sqlite3"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    database = Database(app.config["DATABASE"])
    database.initialize(PROJECT_ROOT / "data" / "products.json")
    product_repository = ProductRepository(database)
    customer_repository = CustomerRepository(database)
    category_repository = CategoryRepository(database)
    cart_repository = CartRepository(database)
    order_repository = OrderRepository(database)
    search_history_repository = SearchHistoryRepository(database)
    vector_index = VectorIndex(PROJECT_ROOT / "static")
    search_service = SearchService(
        product_repository, RankingService(), vector_index, category_repository
    )
    query_service = QueryService(search_service, search_history_repository)
    speech_service = SpeechService(query_service)
    file_storage = FileStorage(PROJECT_ROOT / "static" / "uploads")
    services = {
        "auth": AuthService(customer_repository),
        "admin": AdminService(
            product_repository, category_repository, PROJECT_ROOT / "static"
        ),
        "cart": CartService(database, product_repository, cart_repository),
        "orders": OrderService(
            database,
            product_repository,
            cart_repository,
            order_repository,
            customer_repository,
        ),
        "query": query_service,
        "search": search_service,
        "catalog": ProductService(product_repository),
        "search_history": SearchHistoryService(search_history_repository),
        "speech": speech_service,
        "image": ImageService(
            query_service,
            file_storage,
            vector_index,
            PROJECT_ROOT / "static",
        ),
    }
    app.extensions["shop_services"] = services
    register_controllers(app)

    @app.context_processor
    def navigation_context():
        customer = current_customer()
        cart_count = 0
        if customer:
            cart = services["cart"].get_cart(customer["customer_id"])
            cart_count = sum(item["quantity"] for item in cart["items"])
        return {"current_customer": customer, "cart_count": cart_count}

    @app.errorhandler(RequestEntityTooLarge)
    def upload_too_large(_error):
        from flask import flash, redirect, url_for

        flash("Image uploads must be no larger than 5 MB.", "error")
        return redirect(url_for("home"))

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8080, debug=False)
