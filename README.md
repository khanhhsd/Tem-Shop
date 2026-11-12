
- Email: [admin@example.com](mailto:admin@example.com)
- Password: admin1234

# Tem Shop — local e-commerce demo

A three-layer Flask e-commerce application with a local SQLite database. It includes a 23-product seeded catalog, account registration and login, keyword/voice/image search, cart and checkout, order history, and a small admin area. No database server or external service is required.

## Requirements

- Python 3.10 or later
- Windows, macOS, or Linux

## Project structure

```text
E-Commerce demo/
├── application/               # Business logic and service layer
│   ├── admin_service.py
│   ├── auth_service.py
│   ├── cart_service.py
│   ├── file_storage.py
│   ├── image_service.py
│   ├── order_service.py
│   ├── product_service.py
│   ├── query_service.py
│   ├── ranking_service.py
│   ├── search_history_service.py
│   ├── search_service.py
│   ├── speech_service.py
│   └── vector_index.py
├── data/                      # SQLite schema, repositories, and seed data
│   ├── cart_repository.py
│   ├── category_repository.py
│   ├── customer_repository.py
│   ├── database.py
│   ├── order_repository.py
│   ├── product_repository.py
│   ├── products.json
│   ├── schema.sql
│   └── search_history_repository.py
├── instance/                  # Local runtime SQLite database output
│   └── shop.sqlite3
├── shop/                      # Installable Python package entry points
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py
│   └── cli.py
├── static/                    # CSS, JS, images, uploads, and product assets
│   ├── app.js
│   ├── style.css
│   ├── assets/
│   ├── products/
│   └── uploads/
├── templates/                 # Flask Jinja templates for the storefront
│   ├── admin.html
│   ├── base.html
│   ├── cart.html
│   ├── checkout.html
│   ├── index.html
│   ├── login.html
│   ├── not_found.html
│   ├── orders.html
│   ├── product.html
│   ├── register.html
│   └── ...
├── tests/                     # Automated application tests
│   └── test_shop.py
├── main.py                    # Flask application factory and routes
├── pyproject.toml             # Package metadata and install settings
├── README.md
├── requirements.txt
├── project_explanation.txt
├── Tailieu/                   # Project documentation and assignment assets
│   └── ...
└── .
```

## Run locally

From the project directory:

```powershell
python -m pip install -r requirements.txt
python main.py
```

You can also install the project as a package and run it through the package entry point:

```powershell
python -m pip install -e .
tem-shop
```

Open [http://localhost:8080](http://localhost:8080). Stop the server with `Ctrl+C`.

The SQLite database is created automatically at `instance/shop.sqlite3` on first startup. The schema is in `data/schema.sql`; startup seeds four categories, the 23 products from `data/products.json`, and the local admin account. On every app start, catalog details such as name, description, image, and price are refreshed from `products.json`; stock levels are preserved. Catalog photographs are in `static/products/`; uploaded search images are normalized and saved under `static/uploads/`. The three added collectibles remain at the bottom of the catalog, including relevance-ranked searches.

To run the tests:

```powershell
python -m unittest discover -s tests -v
```

## Demo accounts

- Store admin: `admin@example.com` / `admin1234`
- Shopper: create an account from the site

The admin account is for local demonstration only. Change the password before exposing the app beyond your machine. Set `SECRET_KEY` in the environment to replace the development session key.

## Features

- Register, log in, and log out. Passwords are stored as Werkzeug password hashes.
- Browse and search products by keyword, category, price range, and availability.
- Voice search uses browser Web Speech recognition when supported; the recognized transcript goes through the same query service and is saved in search history. Typed voice transcripts are also supported.
- Image search validates and stores an uploaded image, computes a 12-value RGB color histogram, and ranks catalog images by cosine similarity. This is a simple visual demo, not semantic image recognition.
- Add products to a customer cart, change quantities, remove items, and view totals.
- Checkout creates an order, order items, a payment record, and standard shipping; it checks and decrements stock and clears the cart atomically.
- The checkout's credit-card option is a local demo only. It does not process a charge or connect to a payment provider; only a masked card number is stored. Cash on delivery is also supported.
- View order status and recent searches. The admin can add products from the included image catalog and update stock.

## Architecture

- **Presentation** — Flask routes in `main.py` and Jinja pages in `templates/`. Routes call application services.
- **Application** — `application/` contains auth, catalog search/ranking, speech and image search, cart, checkout, and admin services.
- **Data** — `data/` contains SQLite schema/initialization and repositories for customers, products, carts, orders, categories, and search history. Local image uploads use `application/file_storage.py`.

The database also includes voice/image search detail tables and Payment/Shipping records. Customer subtype fields (VIP/New) and payment subtype fields (credit/cash) are represented in the local schema.
