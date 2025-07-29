from flask import request, jsonify, current_app
from models import *
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import sqlite3
import pandas as pd

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        conn = sqlite3.connect('ecommerce.db')
        
        # Base query
        query = """
        SELECT id, name, description, price, image_url, rating, category_name, stock
        FROM products
        WHERE 1=1
        """
        params = []
        
        # Add filters
        if category:
            query += " AND category_name LIKE ?"
            params.append(f"%{category}%")
        
        if search:
            query += " AND (name LIKE ? OR description LIKE ? OR category_name LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        
        # Add pagination
        offset = (page - 1) * per_page
        query += " ORDER BY rating DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        
        products = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return jsonify({
            'products': products.to_dict('records'),
            'page': page,
            'per_page': per_page,
            'total': len(products)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product details"""
    try:
        conn = sqlite3.connect('ecommerce.db')
        query = """
        SELECT id, name, description, price, image_url, rating, category_name, stock
        FROM products
        WHERE id = ?
        """
        
        product = pd.read_sql_query(query, conn, params=[product_id])
        conn.close()
        
        if product.empty:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify(product.to_dict('records')[0])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>/recommendations', methods=['GET'])
def get_product_recommendations(product_id):
    """Get recommendations for a specific product"""
    try:
        recommendations = recommender.get_similar_products(product_id, 6)
        return jsonify({'recommendations': recommendations})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        conn = sqlite3.connect('ecommerce.db')
        query = """
        SELECT DISTINCT category_name, COUNT(*) as count
        FROM products
        WHERE category_name IS NOT NULL
        GROUP BY category_name
        ORDER BY count DESC
        """
        
        categories = pd.read_sql_query(query, conn)
        conn.close()
        
        return jsonify({'categories': categories.to_dict('records')})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get personalized recommendations for user"""
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        if user_id == 'anonymous':
            # Return popular products for anonymous users
            recommendations = recommender.get_popular_products(10)
        else:
            # Get personalized recommendations
            recommendations = recommender.get_recommendations_for_user(user_id, 10)
        
        return jsonify({'recommendations': recommendations})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Check if user exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        user = User(
            id=f"user_{len(User.query.all()) + 1}",
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            customer_city=data.get('city', ''),
            customer_state=data.get('state', ''),
            customer_zip_code=data.get('zip_code', '')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = jwt.encode({
            'user_id': user.id,
            'email': user.email
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'city': user.customer_city,
                'state': user.customer_state
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and check_password_hash(user.password_hash, data['password']):
            token = jwt.encode({
                'user_id': user.id,
                'email': user.email
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'city': user.customer_city,
                    'state': user.customer_state
                }
            })
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(current_user_id):
    """Get user's cart items"""
    try:
        conn = sqlite3.connect('ecommerce.db')
        query = """
        SELECT ci.id, ci.quantity, p.id as product_id, p.name, p.price, p.image_url
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id = ?
        """
        
        cart_items = pd.read_sql_query(query, conn, params=[current_user_id])
        conn.close()
        
        total = sum(item['price'] * item['quantity'] for _, item in cart_items.iterrows())
        
        return jsonify({
            'items': cart_items.to_dict('records'),
            'total': total,
            'count': len(cart_items)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/add', methods=['POST'])
@token_required
def add_to_cart(current_user_id):
    """Add item to cart"""
    try:
        data = request.get_json()
        product_id = data['product_id']
        quantity = data.get('quantity', 1)
        
        # Check if item already in cart
        existing_item = CartItem.query.filter_by(
            user_id=current_user_id,
            product_id=product_id
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            cart_item = CartItem(
                user_id=current_user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({'message': 'Item added to cart successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/update/<int:item_id>', methods=['PUT'])
@token_required
def update_cart_item(current_user_id, item_id):
    """Update cart item quantity"""
    try:
        data = request.get_json()
        quantity = data['quantity']
        
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=current_user_id
        ).first()
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        if quantity <= 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = quantity
        
        db.session.commit()
        
        return jsonify({'message': 'Cart updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
@token_required
def remove_from_cart(current_user_id, item_id):
    """Remove item from cart"""
    try:
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=current_user_id
        ).first()
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'message': 'Item removed from cart'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'E-commerce API is running',
        'recommender_trained': recommender.is_trained if 'recommender' in globals() else False
    })
