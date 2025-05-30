from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Product, RestockLog
from config import Config
from datetime import datetime, timedelta

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object(Config)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})
db.init_app(app)

# -------------------- PRODUCTS --------------------
@app.route('/api/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'GET':
        return get_products()
    elif request.method == 'POST':
        return add_product()
    else:
        return jsonify({'error': 'Method Not Allowed'}), 405

def get_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200

def add_product():
    data = request.get_json()
    try:
        new_product = Product(
            name=data['name'],
            sku=data['sku'],
            stock_level=data.get('stock_level', 0),
            category=data.get('category'),
            price=data.get('price'),
            cost=data.get('cost')
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field {e}"}), 400

@app.route('/api/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'GET':
        return jsonify(product.to_dict()), 200
    elif request.method == 'PUT':
        return update_product(product)
    elif request.method == 'DELETE':
        return delete_product(product)
    else:
        return jsonify({'error': 'Method Not Allowed'}), 405

def update_product(product):
    data = request.get_json()
    try:
        product.name = data['name']
        product.sku = data['sku']
        product.category = data.get('category')
        product.price = data.get('price')
        product.cost = data.get('cost')
        product.stock_level = data.get('stock_level', product.stock_level)
        db.session.commit()
        return jsonify(product.to_dict()), 200
    except KeyError as e:
        return jsonify({"error": f"Missing field {e}"}), 400

def delete_product(product):
    db.session.delete(product)
    db.session.commit()
    return jsonify({'result': True}), 204

# -------------------- RESTOCK --------------------
@app.route('/api/products/<int:product_id>/restock', methods=['POST'])
def restock_product(product_id):
    data = request.get_json()
    product = Product.query.get_or_404(product_id)
    try:
        quantity = data['quantity']
        product.stock_level += quantity
        db.session.add(product)
        db.session.add(RestockLog(product_id=product_id, quantity=quantity))
        db.session.commit()
        return jsonify(product.to_dict()), 200
    except KeyError as e:
        return jsonify({"error": f"Missing field {e}"}), 400

@app.route('/api/restocks', methods=['GET'])
def get_restock_logs():
    logs = RestockLog.query.order_by(RestockLog.timestamp.desc()).limit(5).all()
    return jsonify([log.to_dict() for log in logs]), 200

# -------------------- DASHBOARD --------------------
@app.route('/api/products/low-stock', methods=['GET'])
def low_stock_products():
    threshold = 10
    low_stock = Product.query.filter(Product.stock_level < threshold).all()
    return jsonify([product.to_dict() for product in low_stock]), 200

@app.route('/api/dashboard/summary', methods=['GET'])
def dashboard_summary():
    products = Product.query.all()
    totalProducts = len(products)
    totalValue = sum((p.price or 0) * (p.stock_level or 0) for p in products)
    lowStockThreshold = 10
    lowStockProducts = len([p for p in products if (p.stock_level or 0) < lowStockThreshold])

    since = datetime.utcnow() - timedelta(days=1)
    restocksPendingCount = RestockLog.query.filter(RestockLog.timestamp >= since).count()

    return jsonify({
        "totalProducts": totalProducts,
        "totalValue": totalValue,
        "lowStockProducts": lowStockProducts,
        "restocksPending": restocksPendingCount
    })

# -------------------- ANALYTICS --------------------
@app.route('/api/analytics/inventory-trend', methods=['GET'])
def inventory_trend():
    today = datetime.utcnow().date()
    trend_data = []
    total_stock = sum(p.stock_level or 0 for p in Product.query.all())

    for i in range(30):
        day = today - timedelta(days=29 - i)
        trend_data.append({
            "date": day.isoformat(),
            "stock": total_stock
        })

    return jsonify(trend_data), 200

@app.route('/api/analytics/product-trend/<int:product_id>', methods=['GET'])
def product_trend(product_id):
    product = Product.query.get_or_404(product_id)
    today = datetime.utcnow().date()
    trends = []

    # simulate: increase stock over 30 days
    for i in range(30):
        day = today - timedelta(days=29 - i)
        simulated_stock = max(product.stock_level - (29 - i), 0)
        trends.append({
            "date": day.isoformat(),
            "stock": simulated_stock
        })

    return jsonify(trends), 200

@app.route('/api/analytics/metrics', methods=['GET'])
def inventory_metrics():
    products = Product.query.all()
    result = []

    for product in products:
        stock_values = [
            max(product.stock_level - (29 - i), 0)
            for i in range(30)
        ]
        current_stock = stock_values[-1]
        min_stock = min(stock_values)
        max_stock = max(stock_values)
        first_stock = stock_values[0]
        change = current_stock - first_stock
        change_percent = round((change / first_stock) * 100, 1) if first_stock > 0 else "N/A"

        result.append({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "currentStock": current_stock,
            "minStock": min_stock,
            "maxStock": max_stock,
            "changeAmount": change,
            "changePercent": change_percent
        })

    return jsonify(result), 200

# -------------------- MAIN --------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='localhost', port=5000, debug=True)
