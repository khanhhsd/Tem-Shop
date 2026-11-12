from flask import current_app, flash, redirect, render_template, request, url_for

from controllers.helpers import admin_required


def register_routes(app):
    @app.get("/admin")
    @admin_required
    def admin():
        services = current_app.extensions["shop_services"]
        return render_template(
            "admin.html",
            products=services["admin"].all_products(),
            categories=services["admin"].categories(),
            image_files=services["admin"].image_files(),
        )

    @app.post("/admin/products")
    @admin_required
    def admin_add_product():
        services = current_app.extensions["shop_services"]
        try:
            price = float(request.form.get("price", ""))
            stock = int(request.form.get("stock", ""))
            category_id = int(request.form.get("category_id", ""))
            services["admin"].add_product(
                request.form.get("name", ""),
                request.form.get("description", ""),
                price,
                stock,
                f"products/{request.form.get('image_file', '')}",
                request.form.get("color", ""),
                category_id,
            )
            flash("Product added to the catalog.", "success")
        except (ValueError, TypeError) as exc:
            flash(str(exc) or "Enter valid product details.", "error")
        return redirect(url_for("admin"))

    @app.post("/admin/stock/<int:product_id>")
    @admin_required
    def admin_update_stock(product_id):
        services = current_app.extensions["shop_services"]
        try:
            stock = int(request.form.get("stock", ""))
            services["admin"].update_stock(product_id, stock)
            flash("Stock updated.", "success")
        except (ValueError, TypeError) as exc:
            flash(str(exc) or "Enter a valid stock quantity.", "error")
        return redirect(url_for("admin"))
