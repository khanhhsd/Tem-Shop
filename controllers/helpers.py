import math
from functools import wraps

from flask import current_app, flash, redirect, request, session, url_for


def get_services():
    return current_app.extensions["shop_services"]


def current_customer():
    customer_id = session.get("customer_id")
    if not customer_id:
        return None
    return get_services()["auth"].get_customer(customer_id)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_customer():
            flash("Please log in to continue.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        customer = current_customer()
        if not customer:
            flash("Log in with the local admin account to open the admin page.", "error")
            return redirect(url_for("login", next=request.path))
        if not customer["is_admin"]:
            flash("This page is available to the local admin account only.", "error")
            return redirect(url_for("home"))
        return view(*args, **kwargs)

    return wrapped


def read_filters():
    filters = {"in_stock": request.values.get("in_stock") == "1"}
    raw_category = request.values.get("category", "")
    try:
        filters["category_id"] = int(raw_category) if raw_category else None
    except ValueError:
        filters["category_id"] = None
        flash("That category filter was not recognized.", "error")
    for field in ("min_price", "max_price"):
        raw_value = request.values.get(field, "").strip()
        try:
            value = float(raw_value) if raw_value else None
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError
            filters[field] = value
        except ValueError:
            filters[field] = None
            if raw_value:
                flash("Price filters must be non-negative numbers.", "error")
    return filters
