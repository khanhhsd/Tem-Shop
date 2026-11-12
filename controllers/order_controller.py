from flask import current_app, flash, redirect, render_template, request, url_for

from controllers.helpers import current_customer, login_required


def register_routes(app):
    @app.get("/checkout")
    @login_required
    def checkout():
        customer = current_customer()
        services = current_app.extensions["shop_services"]
        cart_data = services["cart"].get_cart(customer["customer_id"])
        if not cart_data["items"]:
            flash("Add an item before checking out.", "error")
            return redirect(url_for("cart"))
        return render_template("checkout.html", cart=cart_data, customer=customer)

    @app.post("/checkout")
    @login_required
    def checkout_post():
        services = current_app.extensions["shop_services"]
        try:
            order_id = services["orders"].checkout(
                current_customer()["customer_id"],
                request.form.get("shipping_address", ""),
                request.form.get("payment_method", ""),
                request.form.get("card_number", ""),
                request.form.get("card_holder_name", ""),
                request.form.get("cash_received", 0),
            )
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("checkout"))
        flash(f"Order #{order_id} placed successfully.", "success")
        return redirect(url_for("orders"))

    @app.get("/orders")
    @login_required
    def orders():
        customer_id = current_customer()["customer_id"]
        services = current_app.extensions["shop_services"]
        return render_template(
            "orders.html",
            orders=services["orders"].list_for_customer(customer_id),
            searches=services["search_history"].recent_for_customer(customer_id),
        )
