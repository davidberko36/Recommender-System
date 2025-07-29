from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    product = db.relationship('Product', backref='cart_items')

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='wishlist_items')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product', backref='order_items')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(
        email=data['email'],
        name=data.get('username', data.get('name', '')),
        password_hash=generate_password_hash(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'access_token': token, 
            'user': {
                'id': user.id, 
                'username': user.name, 
                'email': user.email
            }
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Product.query
    
    if category:
        query = query.filter(Product.category == category)
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'products': [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'category': p.category,
            'image_url': p.image_url,
            'rating': p.rating,
            'stock': p.stock
        } for p in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    })

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'category': product.category,
        'image_url': product.image_url,
        'rating': product.rating,
        'stock': product.stock
    })

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import sqlite3
from collections import defaultdict

def get_content_based_recommendations(product_id, limit=5):
    try:
        # Use the correct database path
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')
        conn = sqlite3.connect(db_path)
        
        products_df = pd.read_sql_query(
            "SELECT id, name, description, category, price, rating FROM product", 
            conn
        )
        
        if products_df.empty or product_id not in products_df['id'].values:
            conn.close()
            return get_popular_products(limit)
        
        products_df['content'] = (
            products_df['category'].fillna('') + ' ' + 
            products_df['description'].fillna('')
        )
        
        tfidf = TfidfVectorizer(max_features=100, stop_words='english')
        content_matrix = tfidf.fit_transform(products_df['content'])
        
        product_idx = products_df[products_df['id'] == product_id].index[0]
        content_sim = cosine_similarity(content_matrix[product_idx:product_idx+1], content_matrix).flatten()
        
        similar_indices = content_sim.argsort()[::-1][1:limit+1]
        recommended_products = products_df.iloc[similar_indices]
        
        conn.close()
        
        return [{
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'price': row['price'],
            'category': row['category'],
            'rating': row['rating']
        } for _, row in recommended_products.iterrows()]
        
    except Exception as e:
        print(f"Content-based recommendation error: {e}")
        return get_popular_products(limit)

def get_collaborative_recommendations(user_id, limit=10):
    try:
        # Use the correct database path
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')
        conn = sqlite3.connect(db_path)
        
        interactions_df = pd.read_sql_query("""
            SELECT oi.user_id, oi.product_id, COUNT(*) as interactions
            FROM order_item oi
            JOIN 'order' o ON oi.order_id = o.id
            WHERE o.user_id IS NOT NULL
            GROUP BY oi.user_id, oi.product_id
        """, conn)
        
        if interactions_df.empty:
            conn.close()
            return get_popular_products(limit)
        
        user_item_matrix = interactions_df.pivot_table(
            index='user_id', 
            columns='product_id', 
            values='interactions', 
            fill_value=0
        )
        
        if user_id not in user_item_matrix.index:
            conn.close()
            return get_popular_products(limit)
        
        item_similarity = cosine_similarity(user_item_matrix.T)
        item_similarity_df = pd.DataFrame(
            item_similarity, 
            index=user_item_matrix.columns, 
            columns=user_item_matrix.columns
        )
        
        user_items = user_item_matrix.loc[user_id]
        purchased_items = user_items[user_items > 0].index.tolist()
        
        recommendations = defaultdict(float)
        
        for item in purchased_items:
            if item in item_similarity_df.index:
                similar_items = item_similarity_df[item].sort_values(ascending=False)
                for similar_item, similarity in similar_items.head(20).items():
                    if similar_item not in purchased_items and similarity > 0.1:
                        recommendations[similar_item] += similarity
        
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        recommended_product_ids = [item[0] for item in sorted_recommendations[:limit]]
        
        products_df = pd.read_sql_query(
            f"SELECT id, name, description, price, category, rating FROM product WHERE id IN ({','.join(map(str, recommended_product_ids))})", 
            conn
        )
        
        conn.close()
        
        return [{
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'price': row['price'],
            'category': row['category'],
            'rating': row['rating']
        } for _, row in products_df.iterrows()]
        
    except Exception as e:
        print(f"Collaborative filtering error: {e}")
        return get_popular_products(limit)

def get_popular_products(limit=10):
    try:
        # Use the correct database path
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')
        conn = sqlite3.connect(db_path)
        
        popular_df = pd.read_sql_query(f"""
            SELECT p.id, p.name, p.description, p.price, p.category, p.rating,
                   COALESCE(order_counts.order_count, 0) as order_count
            FROM product p
            LEFT JOIN (
                SELECT oi.product_id, COUNT(*) as order_count
                FROM order_item oi
                GROUP BY oi.product_id
            ) order_counts ON p.id = order_counts.product_id
            ORDER BY p.rating DESC, order_counts.order_count DESC
            LIMIT {limit}
        """, conn)
        
        conn.close()
        
        return [{
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'price': row['price'],
            'category': row['category'],
            'rating': row['rating']
        } for _, row in popular_df.iterrows()]
        
    except Exception as e:
        print(f"Popular products error: {e}")
        return []

@app.route('/api/products/<int:product_id>/recommendations', methods=['GET'])
def get_product_recommendations(product_id):
    recommendations = get_content_based_recommendations(product_id, limit=6)
    return jsonify({'recommendations': recommendations})

@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(current_user):
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'cart_items': [{
            'id': item.id,
            'product': {
                'id': item.product.id,
                'name': item.product.name,
                'description': item.product.description,
                'price': item.product.price,
                'category': item.product.category,
                'image_url': item.product.image_url
            },
            'quantity': item.quantity
        } for item in cart_items]
    })

@app.route('/api/cart', methods=['POST'])
@token_required
def add_to_cart(current_user):
    data = request.get_json()
    product_id = data['product_id']
    quantity = data.get('quantity', 1)
    
    existing_item = CartItem.query.filter_by(
        user_id=current_user.id, 
        product_id=product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    return jsonify({'message': 'Item added to cart'}), 201

@app.route('/api/cart', methods=['PUT'])
@token_required
def update_cart(current_user):
    data = request.get_json()
    item_id = data['item_id']
    quantity = data['quantity']
    
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    item.quantity = quantity
    db.session.commit()
    
    return jsonify({'message': 'Cart item updated'}), 200

@app.route('/api/cart', methods=['DELETE'])
@token_required
def remove_from_cart(current_user):
    data = request.get_json()
    item_id = data['item_id']
    
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'})

@app.route('/api/wishlist', methods=['GET'])
@token_required
def get_wishlist(current_user):
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'wishlist_items': [{
            'id': item.id,
            'product': {
                'id': item.product.id,
                'name': item.product.name,
                'description': item.product.description,
                'price': item.product.price,
                'category': item.product.category,
                'image_url': item.product.image_url
            }
        } for item in wishlist_items]
    })

@app.route('/api/wishlist', methods=['POST'])
@token_required
def add_to_wishlist(current_user):
    data = request.get_json()
    product_id = data['product_id']
    
    existing_item = WishlistItem.query.filter_by(
        user_id=current_user.id, 
        product_id=product_id
    ).first()
    
    if existing_item:
        return jsonify({'message': 'Item already in wishlist'}), 400
    
    wishlist_item = WishlistItem(
        user_id=current_user.id,
        product_id=product_id
    )
    
    db.session.add(wishlist_item)
    db.session.commit()
    return jsonify({'message': 'Item added to wishlist'}), 201

@app.route('/api/wishlist', methods=['DELETE'])
@token_required
def remove_from_wishlist(current_user):
    data = request.get_json()
    item_id = data['item_id']
    
    item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item removed from wishlist'})

@app.route('/api/orders', methods=['POST'])
@token_required
def create_order(current_user):
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        return jsonify({'message': 'Cart is empty'}), 400
    
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount
    )
    db.session.add(order)
    db.session.commit()
    
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.session.add(order_item)
        db.session.delete(cart_item)
    
    db.session.commit()
    return jsonify({'message': 'Order created successfully', 'order_id': order.id}), 201

@app.route('/api/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify({
        'orders': [{
            'id': order.id,
            'total_amount': order.total_amount,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'items': [{
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'category': item.product.category
                },
                'quantity': item.quantity,
                'price': item.price
            } for item in order.order_items]
        } for order in orders]
    })

@app.route('/api/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user):
    limit = request.args.get('limit', 10, type=int)
    
    try:
        # Try collaborative filtering first
        collaborative_recs = get_collaborative_recommendations(current_user.id, limit)
        
        if collaborative_recs and len(collaborative_recs) > 0:
            print(f"Returning {len(collaborative_recs)} collaborative recommendations for user {current_user.id}")
            return jsonify({'recommendations': collaborative_recs})
        else:
            # Fallback to popular products
            print(f"No collaborative recommendations found for user {current_user.id}, falling back to popular products")
            popular_recs = get_popular_products(limit)
            return jsonify({'recommendations': popular_recs})
    except Exception as e:
        print(f"Error in recommendations endpoint: {e}")
        # Fallback to popular products in case of any error
        popular_recs = get_popular_products(limit)
        return jsonify({'recommendations': popular_recs})

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    limit = request.args.get('limit', 10, type=int)
    recommendations = get_collaborative_recommendations(user_id, limit)
    return jsonify({'recommendations': recommendations})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = db.session.query(Product.category).distinct().all()
    return jsonify({'categories': [cat[0] for cat in categories]})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Backend API is running with expanded catalog'})

def init_sample_data():
    # Clear existing products and re-initialize with expanded catalog
    existing_count = Product.query.count()
    if existing_count < 10:  # Only initialize if we have fewer than 10 products
        if existing_count > 0:
            print(f"Clearing {existing_count} existing products...")
            Product.query.delete()
            db.session.commit()
            
        sample_products = [
            # Electronics
            {'name': 'Wireless Headphones', 'description': 'High-quality bluetooth headphones with noise cancellation', 'price': 99.99, 'category': 'Electronics', 'image_url': 'https://picsum.photos/300/300?random=1', 'rating': 4.5, 'stock': 50},
            {'name': 'Smart Watch', 'description': 'Feature-rich smartwatch with fitness tracking', 'price': 199.99, 'category': 'Electronics', 'image_url': 'https://picsum.photos/300/300?random=2', 'rating': 4.3, 'stock': 30},
            {'name': 'Laptop', 'description': 'High-performance laptop for work and gaming', 'price': 1299.99, 'category': 'Electronics', 'image_url': 'https://picsum.photos/300/300?random=3', 'rating': 4.7, 'stock': 15},
            {'name': 'Smartphone', 'description': 'Latest flagship smartphone with advanced camera', 'price': 799.99, 'category': 'Electronics', 'image_url': 'https://picsum.photos/300/300?random=4', 'rating': 4.6, 'stock': 25},
            {'name': 'Bluetooth Speaker', 'description': 'Portable bluetooth speaker with rich bass', 'price': 59.99, 'category': 'Electronics', 'image_url': 'https://picsum.photos/300/300?random=5', 'rating': 4.2, 'stock': 60},
            {'name': 'Gaming Mouse', 'description': 'Precision gaming mouse with RGB lighting', 'price': 79.99, 'category': 'Electronics', 'image_url': 'https://picsum.photos/300/300?random=6', 'rating': 4.4, 'stock': 40},
            {'name': 'Wireless Keyboard', 'description': 'Mechanical wireless keyboard for productivity', 'price': 129.99, 'category': 'Electronics', 'image_url': 'https://picsum.photos/300/300?random=7', 'rating': 4.5, 'stock': 35},
            
            # Home & Kitchen
            {'name': 'Coffee Maker', 'description': 'Automatic drip coffee maker with timer', 'price': 79.99, 'category': 'Home & Kitchen', 'image_url': 'https://picsum.photos/300/300?random=8', 'rating': 4.1, 'stock': 25},
            {'name': 'Air Fryer', 'description': 'Digital air fryer for healthy cooking', 'price': 119.99, 'category': 'Home & Kitchen', 'image_url': 'https://picsum.photos/300/300?random=9', 'rating': 4.6, 'stock': 30},
            {'name': 'Blender', 'description': 'High-speed blender for smoothies and soups', 'price': 89.99, 'category': 'Home & Kitchen', 'image_url': 'https://picsum.photos/300/300?random=10', 'rating': 4.3, 'stock': 20},
            {'name': 'Stand Mixer', 'description': 'Professional stand mixer for baking', 'price': 299.99, 'category': 'Home & Kitchen', 'image_url': 'https://picsum.photos/300/300?random=11', 'rating': 4.8, 'stock': 12},
            {'name': 'Vacuum Cleaner', 'description': 'Cordless vacuum cleaner with powerful suction', 'price': 249.99, 'category': 'Home & Kitchen', 'image_url': 'https://picsum.photos/300/300?random=12', 'rating': 4.4, 'stock': 18},
            {'name': 'Rice Cooker', 'description': 'Smart rice cooker with multiple cooking modes', 'price': 69.99, 'category': 'Home & Kitchen', 'image_url': 'https://picsum.photos/300/300?random=13', 'rating': 4.2, 'stock': 45},
            
            # Sports & Fitness
            {'name': 'Running Shoes', 'description': 'Comfortable running shoes with cushioning', 'price': 89.99, 'category': 'Sports & Fitness', 'image_url': 'https://picsum.photos/300/300?random=14', 'rating': 4.4, 'stock': 40},
            {'name': 'Yoga Mat', 'description': 'Non-slip yoga mat for exercise and meditation', 'price': 29.99, 'category': 'Sports & Fitness', 'image_url': 'https://picsum.photos/300/300?random=15', 'rating': 4.3, 'stock': 75},
            {'name': 'Dumbbells Set', 'description': 'Adjustable dumbbells for strength training', 'price': 199.99, 'category': 'Sports & Fitness', 'image_url': 'https://picsum.photos/300/300?random=16', 'rating': 4.5, 'stock': 20},
            {'name': 'Fitness Tracker', 'description': 'Waterproof fitness tracker with heart rate monitor', 'price': 149.99, 'category': 'Sports & Fitness', 'image_url': 'https://picsum.photos/300/300?random=17', 'rating': 4.2, 'stock': 35},
            {'name': 'Resistance Bands', 'description': 'Set of resistance bands for home workouts', 'price': 24.99, 'category': 'Sports & Fitness', 'image_url': 'https://picsum.photos/300/300?random=18', 'rating': 4.1, 'stock': 80},
            {'name': 'Basketball', 'description': 'Official size basketball for indoor and outdoor play', 'price': 39.99, 'category': 'Sports & Fitness', 'image_url': 'https://picsum.photos/300/300?random=19', 'rating': 4.3, 'stock': 50},
            
            # Books
            {'name': 'Python Programming', 'description': 'Complete guide to Python programming', 'price': 29.99, 'category': 'Books', 'image_url': 'https://picsum.photos/300/300?random=20', 'rating': 4.6, 'stock': 100},
            {'name': 'Data Science Handbook', 'description': 'Essential tools and techniques for data science', 'price': 39.99, 'category': 'Books', 'image_url': 'https://picsum.photos/300/300?random=21', 'rating': 4.7, 'stock': 85},
            {'name': 'Machine Learning Guide', 'description': 'Practical introduction to machine learning', 'price': 44.99, 'category': 'Books', 'image_url': 'https://picsum.photos/300/300?random=22', 'rating': 4.5, 'stock': 70},
            {'name': 'Web Development Bible', 'description': 'Complete guide to modern web development', 'price': 34.99, 'category': 'Books', 'image_url': 'https://picsum.photos/300/300?random=23', 'rating': 4.4, 'stock': 90},
            {'name': 'The Art of War', 'description': 'Classic strategy and philosophy book', 'price': 12.99, 'category': 'Books', 'image_url': 'https://picsum.photos/300/300?random=24', 'rating': 4.8, 'stock': 120},
            {'name': 'Cooking Masterclass', 'description': 'Professional cooking techniques and recipes', 'price': 27.99, 'category': 'Books', 'image_url': 'https://picsum.photos/300/300?random=25', 'rating': 4.3, 'stock': 65},
            
            # Clothing & Fashion
            {'name': 'Cotton T-Shirt', 'description': 'Comfortable 100% cotton t-shirt', 'price': 19.99, 'category': 'Clothing & Fashion', 'image_url': 'https://picsum.photos/300/300?random=26', 'rating': 4.2, 'stock': 100},
            {'name': 'Denim Jeans', 'description': 'Classic fit denim jeans', 'price': 59.99, 'category': 'Clothing & Fashion', 'image_url': 'https://picsum.photos/300/300?random=27', 'rating': 4.3, 'stock': 60},
            {'name': 'Winter Jacket', 'description': 'Warm winter jacket with insulation', 'price': 149.99, 'category': 'Clothing & Fashion', 'image_url': 'https://picsum.photos/300/300?random=28', 'rating': 4.6, 'stock': 25},
            {'name': 'Sneakers', 'description': 'Casual sneakers for everyday wear', 'price': 79.99, 'category': 'Clothing & Fashion', 'image_url': 'https://picsum.photos/300/300?random=29', 'rating': 4.4, 'stock': 45},
            {'name': 'Dress Shirt', 'description': 'Formal dress shirt for business occasions', 'price': 49.99, 'category': 'Clothing & Fashion', 'image_url': 'https://picsum.photos/300/300?random=30', 'rating': 4.1, 'stock': 55},
            {'name': 'Leather Belt', 'description': 'Genuine leather belt with metal buckle', 'price': 34.99, 'category': 'Clothing & Fashion', 'image_url': 'https://picsum.photos/300/300?random=31', 'rating': 4.3, 'stock': 70},
            
            # Beauty & Personal Care
            {'name': 'Face Moisturizer', 'description': 'Hydrating face moisturizer for all skin types', 'price': 24.99, 'category': 'Beauty & Personal Care', 'image_url': 'https://picsum.photos/300/300?random=32', 'rating': 4.2, 'stock': 80},
            {'name': 'Electric Toothbrush', 'description': 'Rechargeable electric toothbrush with timer', 'price': 89.99, 'category': 'Beauty & Personal Care', 'image_url': 'https://picsum.photos/300/300?random=33', 'rating': 4.5, 'stock': 35},
            {'name': 'Hair Dryer', 'description': 'Professional hair dryer with multiple settings', 'price': 69.99, 'category': 'Beauty & Personal Care', 'image_url': 'https://picsum.photos/300/300?random=34', 'rating': 4.3, 'stock': 40},
            {'name': 'Perfume', 'description': 'Luxury perfume with long-lasting fragrance', 'price': 79.99, 'category': 'Beauty & Personal Care', 'image_url': 'https://picsum.photos/300/300?random=35', 'rating': 4.4, 'stock': 30},
            {'name': 'Makeup Brush Set', 'description': 'Professional makeup brush set with case', 'price': 39.99, 'category': 'Beauty & Personal Care', 'image_url': 'https://picsum.photos/300/300?random=36', 'rating': 4.6, 'stock': 50},
            
            # Automotive
            {'name': 'Car Phone Mount', 'description': 'Universal phone mount for car dashboard', 'price': 19.99, 'category': 'Automotive', 'image_url': 'https://picsum.photos/300/300?random=37', 'rating': 4.1, 'stock': 85},
            {'name': 'Car Charger', 'description': 'Fast charging car charger with dual USB ports', 'price': 14.99, 'category': 'Automotive', 'image_url': 'https://picsum.photos/300/300?random=38', 'rating': 4.2, 'stock': 100},
            {'name': 'Dash Cam', 'description': 'HD dash cam with night vision', 'price': 89.99, 'category': 'Automotive', 'image_url': 'https://picsum.photos/300/300?random=39', 'rating': 4.4, 'stock': 25},
            {'name': 'Car Air Freshener', 'description': 'Long-lasting car air freshener', 'price': 7.99, 'category': 'Automotive', 'image_url': 'https://picsum.photos/300/300?random=40', 'rating': 3.9, 'stock': 150},
            
            # Toys & Games
            {'name': 'Board Game: Settlers', 'description': 'Strategic board game for family fun', 'price': 49.99, 'category': 'Toys & Games', 'image_url': 'https://picsum.photos/300/300?random=41', 'rating': 4.7, 'stock': 40},
            {'name': 'Puzzle 1000 pieces', 'description': '1000-piece jigsaw puzzle with beautiful artwork', 'price': 19.99, 'category': 'Toys & Games', 'image_url': 'https://picsum.photos/300/300?random=42', 'rating': 4.3, 'stock': 60},
            {'name': 'Remote Control Car', 'description': 'High-speed remote control racing car', 'price': 79.99, 'category': 'Toys & Games', 'image_url': 'https://picsum.photos/300/300?random=43', 'rating': 4.5, 'stock': 30},
            {'name': 'Building Blocks Set', 'description': 'Creative building blocks for kids', 'price': 34.99, 'category': 'Toys & Games', 'image_url': 'https://picsum.photos/300/300?random=44', 'rating': 4.4, 'stock': 45},
            
            # Garden & Outdoor
            {'name': 'Garden Hose', 'description': 'Expandable garden hose with spray nozzle', 'price': 29.99, 'category': 'Garden & Outdoor', 'image_url': 'https://picsum.photos/300/300?random=45', 'rating': 4.1, 'stock': 55},
            {'name': 'Plant Pots Set', 'description': 'Set of ceramic plant pots with drainage', 'price': 24.99, 'category': 'Garden & Outdoor', 'image_url': 'https://picsum.photos/300/300?random=46', 'rating': 4.2, 'stock': 70},
            {'name': 'Garden Tools Kit', 'description': 'Complete set of garden tools with storage', 'price': 59.99, 'category': 'Garden & Outdoor', 'image_url': 'https://picsum.photos/300/300?random=47', 'rating': 4.4, 'stock': 35},
            {'name': 'Camping Tent', 'description': 'Waterproof camping tent for 4 people', 'price': 149.99, 'category': 'Garden & Outdoor', 'image_url': 'https://picsum.photos/300/300?random=48', 'rating': 4.6, 'stock': 20},
            {'name': 'Outdoor Grill', 'description': 'Portable charcoal grill for outdoor cooking', 'price': 89.99, 'category': 'Garden & Outdoor', 'image_url': 'https://picsum.photos/300/300?random=49', 'rating': 4.3, 'stock': 25}
        ]
        
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"Sample data initialized with {len(sample_products)} products across multiple categories")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
