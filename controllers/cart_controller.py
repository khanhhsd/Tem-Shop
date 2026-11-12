from flask import current_app, flash, redirect, render_template, request, url_for

from controllers.helpers import current_customer, login_required


def register_routes(app):
    @app.post("/cart/add/<int:product_id>")
    @login_required
    def cart_add(product_id):
        services = current_app.extensions["shop_services"]
        try:
            quantity = int(request.form.get("quantity", "1"))
            services["cart"].add(current_customer()["customer_id"], product_id, quantity)
            flash("Added to your cart.", "success")
        except (ValueError, TypeError) as exc:
            flash(str(exc), "error")
        return redirect(url_for("product_detail", product_id=product_id))

    @app.get("/cart")
    @login_required
    def cart():
        services = current_app.extensions["shop_services"]
        return render_template(
            "cart.html",
            cart=services["cart"].get_cart(current_customer()["customer_id"]),
        )

    @app.post("/cart/update/<int:product_id>")
    @login_required
    def cart_update(product_id):
        services = current_app.extensions["shop_services"]
        try:
            quantity = int(request.form.get("quantity", "0"))
            services["cart"].update(current_customer()["customer_id"], product_id, quantity)
            flash("Cart quantity updated.", "success")
        except (ValueError, TypeError) as exc:
            flash(str(exc), "error")
        return redirect(url_for("cart"))

    @app.post("/cart/remove/<int:product_id>")
    @login_required
    def cart_remove(product_id):
        services = current_app.extensions["shop_services"]
        try:
            services["cart"].remove(current_customer()["customer_id"], product_id)
            flash("Item removed from your cart.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("cart"))
