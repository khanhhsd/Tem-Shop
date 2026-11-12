import sqlite3

from flask import current_app, flash, redirect, render_template, request, session, url_for

from controllers.helpers import login_required


def register_routes(app):
    @app.get("/register")
    def register():
        return render_template("register.html")

    @app.post("/register")
    def register_post():
        services = current_app.extensions["shop_services"]
        try:
            customer = services["auth"].register(
                request.form.get("name", ""),
                request.form.get("email", ""),
                request.form.get("password", ""),
                request.form.get("phone", ""),
                request.form.get("address", ""),
            )
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("register.html"), 400
        except sqlite3.IntegrityError as exc:
            if "UNIQUE constraint failed: customers.email" not in str(exc):
                raise
            flash("An account with that email already exists.", "error")
            return render_template("register.html"), 400
        session.clear()
        session["customer_id"] = customer["customer_id"]
        flash("Your account is ready. Welcome to Tem Shop!", "success")
        return redirect(url_for("home"))

    @app.get("/login")
    def login():
        return render_template("login.html")

    @app.post("/login")
    def login_post():
        services = current_app.extensions["shop_services"]
        customer = services["auth"].authenticate(
            request.form.get("email", ""),
            request.form.get("password", ""),
        )
        if not customer:
            flash("Email or password was incorrect.", "error")
            return render_template("login.html"), 401
        session.clear()
        session["customer_id"] = customer["customer_id"]
        destination = request.args.get("next", "")
        if not destination.startswith("/") or destination.startswith("//"):
            destination = url_for("home")
        return redirect(destination)

    @app.post("/logout")
    @login_required
    def logout():
        session.clear()
        flash("You are signed out.", "success")
        return redirect(url_for("home"))
