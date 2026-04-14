from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# =========================
# CONFIG
# =========================
UPLOAD_FOLDER = 'static/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# DB CONNECTION
# =========================
def get_db_connection():
    conn = sqlite3.connect('1.db')
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# HOME
# =========================
@app.route('/')
def home():
    return "Backend Running 🚀"


# =========================
# USER REGISTER
# =========================
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, email, phone, password, address)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data['name'],
        data['email'],
        data['phone'],
        data['password'],
        data['address']
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "User Registered"})


# =========================
# USER LOGIN
# =========================
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=? AND password=?",
                   (data['email'], data['password']))

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"user_id": user["id"]})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# =========================
# SELLER REGISTER
# =========================
@app.route('/add_shop', methods=['POST'])
def add_shop():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO shops (shop_name, owner_name, phone, address, latitude, longitude, email, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['shop_name'],
        data['owner_name'],
        data['phone'],
        data['address'],
        data['latitude'],
        data['longitude'],
        data['email'],
        data['password']
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Shop Registered"})


# =========================
# SELLER LOGIN
# =========================
@app.route('/seller_login', methods=['POST'])
def seller_login():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM shops WHERE email=? AND password=?",
                   (data['email'], data['password']))

    seller = cursor.fetchone()
    conn.close()

    if seller:
        return jsonify({"shop_id": seller["shop_id"]})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# =========================
# ADD PRODUCT (IMAGE)
# =========================
@app.route('/add_product', methods=['POST'])
def add_product():

    file = request.files.get('image')

    if not file:
        return jsonify({"error": "Image required"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (shop_id, product_name, category, price, size, stock, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form['shop_id'],
        request.form['product_name'],
        request.form['category'],
        request.form['price'],
        request.form['size'],
        request.form['stock'],
        filepath
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Product Added"})


# =========================
# GET PRODUCTS
# =========================
@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return jsonify([dict(p) for p in products])


# =========================
# PLACE ORDER
# =========================
@app.route('/place_order', methods=['POST'])
def place_order():

    data = request.json

    payment_method = data['payment_method']
    payment_status = "PAID" if payment_method == "UPI" else "PENDING"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders (user_id, shop_id, total_amount, payment_status, payment_method, delivery_address, order_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data['user_id'],
        data['shop_id'],
        data['total_amount'],
        payment_status,
        data['payment_method'],
        data['delivery_address'],
        "PENDING"
    ))

    order_id = cursor.lastrowid

    for item in data['items']:
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (
            order_id,
            item['product_id'],
            item['quantity'],
            item['price']
        ))

    conn.commit()
    conn.close()

    return jsonify({"order_id": order_id})


# =========================
# USER ORDERS
# =========================
@app.route('/user_orders/<int:user_id>', methods=['GET'])
def user_orders(user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE user_id=?", (user_id,))
    orders = cursor.fetchall()

    conn.close()

    return jsonify([dict(o) for o in orders])


# =========================
# SELLER ORDERS
# =========================
@app.route('/seller_orders/<int:shop_id>', methods=['GET'])
def seller_orders(shop_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE shop_id=?", (shop_id,))
    orders = cursor.fetchall()

    conn.close()

    return jsonify([dict(o) for o in orders])


# =========================
# UPDATE ORDER STATUS
# =========================
@app.route('/update_order_status', methods=['POST'])
def update_order_status():

    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders SET order_status=? WHERE order_id=?
    """, (data['status'], data['order_id']))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated"})


# =========================
# TRACK ORDER
# =========================
@app.route('/track_order/<int:order_id>', methods=['GET'])
def track_order(order_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT order_status FROM orders WHERE order_id=?", (order_id,))
    order = cursor.fetchone()

    conn.close()

    if order:
        return jsonify({"order_status": order["order_status"]})
    else:
        return jsonify({"error": "Not found"}), 404


# =========================
# ADMIN ANALYTICS
# =========================
@app.route('/admin_analytics', methods=['GET'])
def admin_analytics():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    orders = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_amount) FROM orders WHERE payment_status='PAID'")
    revenue = cursor.fetchone()[0] or 0

    conn.close()

    return jsonify({
        "users": users,
        "orders": orders,
        "revenue": revenue
    })


# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True)