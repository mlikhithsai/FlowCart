
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    password TEXT,
    address TEXT
);

-- =========================
-- SHOPS TABLE
-- =========================
CREATE TABLE shops (
    shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_name TEXT,
    owner_name TEXT,
    phone TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL
);

-- =========================
-- PRODUCTS TABLE
-- =========================
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_id INTEGER,
    product_name TEXT,
    category TEXT,
    price REAL,
    size TEXT,
    stock INTEGER,
    image_url TEXT,
    FOREIGN KEY (shop_id) REFERENCES shops(shop_id) ON DELETE CASCADE
);

-- =========================
-- ORDERS TABLE
-- =========================
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    shop_id INTEGER,
    total_amount REAL,
    order_status TEXT DEFAULT 'PLACED',
    payment_status TEXT DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (shop_id) REFERENCES shops(shop_id)
);

-- =========================
-- ORDER ITEMS TABLE
-- =========================
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- =========================
-- PAYMENTS TABLE
-- =========================
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    payment_method TEXT,
    payment_status TEXT,
    transaction_id TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- =========================
-- SELLER BANK DETAILS
-- =========================
CREATE TABLE seller_bank_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_id INTEGER,
    account_holder_name TEXT,
    bank_name TEXT,
    account_number TEXT,
    ifsc_code TEXT,
    upi_id TEXT,
    FOREIGN KEY (shop_id) REFERENCES shops(shop_id) ON DELETE CASCADE
);


CREATE TABLE delivery (
    delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    delivery_person_name TEXT,
    delivery_phone TEXT,
    delivery_status TEXT DEFAULT 'ASSIGNED',
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);