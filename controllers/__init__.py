"""MVC controller package for the Tem Shop application."""

from .admin_controller import register_routes as register_admin_routes
from .auth_controller import register_routes as register_auth_routes
from .cart_controller import register_routes as register_cart_routes
from .catalog_controller import register_routes as register_catalog_routes
from .order_controller import register_routes as register_order_routes

__all__ = [
    "register_admin_routes",
    "register_auth_routes",
    "register_cart_routes",
    "register_catalog_routes",
    "register_order_routes",
]
