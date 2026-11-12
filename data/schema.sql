CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    phone TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    customer_type TEXT NOT NULL DEFAULT 'new',
    vip_level INTEGER,
    discount_rate REAL NOT NULL DEFAULT 0,
    welcome_coupon_code TEXT,
    trial_period_end TEXT,
    is_admin INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1))
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    image_url TEXT NOT NULL,
    color TEXT NOT NULL DEFAULT '',
    category_id INTEGER NOT NULL REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS carts (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL UNIQUE REFERENCES customers(customer_id) ON DELETE CASCADE,
    created_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cart_items (
    cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    UNIQUE(cart_id, product_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'Placed',
    total_amount REAL NOT NULL CHECK (total_amount >= 0)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    amount REAL NOT NULL CHECK (amount >= 0),
    payment_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    payment_method TEXT NOT NULL CHECK (payment_method IN ('credit', 'cash')),
    card_number_masked TEXT,
    card_holder_name TEXT,
    received_by TEXT,
    change_given REAL
);

CREATE TABLE IF NOT EXISTS shipping (
    shipping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    shipping_address TEXT NOT NULL,
    shipping_method TEXT NOT NULL,
    shipping_cost REAL NOT NULL DEFAULT 0 CHECK (shipping_cost >= 0),
    estimated_delivery TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS search_histories (
    search_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE SET NULL,
    query_type TEXT NOT NULL CHECK (query_type IN ('text', 'voice', 'image')),
    query_text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS voice_search_queries (
    voice_search_query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_history_id INTEGER NOT NULL UNIQUE REFERENCES search_histories(search_history_id) ON DELETE CASCADE,
    transcript TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS image_search_queries (
    image_search_query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_history_id INTEGER NOT NULL UNIQUE REFERENCES search_histories(search_history_id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    feature_vector TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id, order_date DESC);
CREATE INDEX IF NOT EXISTS idx_search_history_customer ON search_histories(customer_id, created_at DESC);
