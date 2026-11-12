from flask import current_app, flash, redirect, render_template, request, url_for

from controllers.helpers import current_customer, read_filters


def register_routes(app):
    @app.get("/")
    def home():
        services = current_app.extensions["shop_services"]
        query = request.args.get("q", "").strip()
        mode = request.args.get("mode", "text")
        if mode not in {"text", "voice"}:
            mode = "text"
        filters = read_filters()
        customer = current_customer()
        customer_id = customer["customer_id"] if customer else None
        if query and mode == "voice":
            result = services["speech"].search(query, filters, customer_id)
        elif query:
            result = services["query"].text_query(query, filters, customer_id)
        else:
            result = {"type": "text", "query": "", "results": services["search"].browse(filters)}
        return render_template(
            "index.html",
            results=result["results"],
            query=query,
            mode=mode,
            categories=services["search"].categories(),
            filters=filters,
            image_url=None,
        )

    @app.get("/products/<int:product_id>")
    def product_detail(product_id):
        services = current_app.extensions["shop_services"]
        product = services["catalog"].get_product(product_id)
        if not product:
            return render_template("not_found.html"), 404
        return render_template("product.html", product=product)

    @app.post("/search/image")
    def image_search():
        services = current_app.extensions["shop_services"]
        customer = current_customer()
        try:
            result, image_url = services["image"].search(
                request.files.get("image"),
                read_filters(),
                customer["customer_id"] if customer else None,
            )
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("home"))
        return render_template(
            "index.html",
            results=result["results"],
            query="",
            mode="image",
            categories=services["search"].categories(),
            filters=read_filters(),
            image_url=image_url,
        )
