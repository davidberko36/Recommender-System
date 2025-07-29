#!/usr/bin/env python3
"""
Enhanced Backend with Real Olist Data
This server uses the actual Brazilian E-commerce dataset
"""

from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import sqlite3
import pandas as pd
import random

app = Flask(__name__)
CORS(app)

DB_NAME = 'ecommerce_real.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("SELECT COUNT(*) as count FROM products")
        product_count = cursor.fetchone()['count']
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'message': 'Real Olist Backend API is running!',
            'database': f'{product_count} products loaded from Brazilian E-commerce dataset'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get products with optional filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        conn = get_db_connection()
        
        # Build query
        query = """
        SELECT id, name, description, price, category_name, image_url, rating, stock
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
        query += " ORDER BY rating DESC, name ASC LIMIT ? OFFSET ?"
        offset = (page - 1) * per_page
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
        conn = get_db_connection()
        
        query = """
        SELECT id, name, description, price, category_name, image_url, rating, stock,
               weight_g, length_cm, height_cm, width_cm, photos_qty
        FROM products 
        WHERE id = ?
        """
        
        cursor = conn.execute(query, [product_id])
        product = cursor.fetchone()
        conn.close()
        
        if product:
            return jsonify(dict(product))
        else:
            return jsonify({'error': 'Product not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>/recommendations', methods=['GET'])
def get_product_recommendations(product_id):
    """Get recommendations for a specific product"""
    try:
        conn = get_db_connection()
        
        # Get the current product's category
        product_query = "SELECT category_name FROM products WHERE id = ?"
        cursor = conn.execute(product_query, [product_id])
        product = cursor.fetchone()
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        category = product['category_name']
        
        # Get similar products from same category
        rec_query = """
        SELECT id, name, description, price, category_name, image_url, rating, stock
        FROM products 
        WHERE category_name = ? AND id != ?
        ORDER BY rating DESC, RANDOM()
        LIMIT 6
        """
        
        recommendations = pd.read_sql_query(rec_query, conn, params=[category, product_id])
        conn.close()
        
        return jsonify({'recommendations': recommendations.to_dict('records')})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get personalized recommendations"""
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        conn = get_db_connection()
        
        if user_id != 'anonymous':
            # Get personalized recommendations based on user's order history
            query = """
            SELECT DISTINCT p.id, p.name, p.description, p.price, p.category_name, 
                   p.image_url, p.rating, p.stock
            FROM products p
            JOIN order_items oi ON p.id = oi.product_id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.customer_id != ?
            AND p.category_name IN (
                SELECT DISTINCT p2.category_name
                FROM products p2
                JOIN order_items oi2 ON p2.id = oi2.product_id
                JOIN orders o2 ON oi2.order_id = o2.id
                WHERE o2.customer_id = ?
            )
            ORDER BY p.rating DESC, RANDOM()
            LIMIT 10
            """
            recommendations = pd.read_sql_query(query, conn, params=[user_id, user_id])
        else:
            # Get popular products for anonymous users
            query = """
            SELECT p.id, p.name, p.description, p.price, p.category_name, 
                   p.image_url, p.rating, p.stock,
                   COUNT(oi.product_id) as purchase_count
            FROM products p
            LEFT JOIN order_items oi ON p.id = oi.product_id
            GROUP BY p.id
            ORDER BY p.rating DESC, purchase_count DESC, RANDOM()
            LIMIT 10
            """
            recommendations = pd.read_sql_query(query, conn)
        
        conn.close()
        
        return jsonify({'recommendations': recommendations.to_dict('records')})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        conn = get_db_connection()
        
        query = """
        SELECT category_name, COUNT(*) as count
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

@app.route('/api/search', methods=['GET'])
def search_products():
    """Advanced product search"""
    try:
        query_text = request.args.get('q', '')
        category = request.args.get('category', '')
        min_price = request.args.get('min_price', 0, type=float)
        max_price = request.args.get('max_price', 10000, type=float)
        min_rating = request.args.get('min_rating', 0, type=float)
        
        conn = get_db_connection()
        
        query = """
        SELECT id, name, description, price, category_name, image_url, rating, stock
        FROM products 
        WHERE price BETWEEN ? AND ?
        AND rating >= ?
        """
        params = [min_price, max_price, min_rating]
        
        if query_text:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{query_text}%", f"%{query_text}%"])
        
        if category:
            query += " AND category_name = ?"
            params.append(category)
        
        query += " ORDER BY rating DESC, price ASC LIMIT 50"
        
        results = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return jsonify({
            'results': results.to_dict('records'),
            'total': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        
        stats = {}
        
        # Product count
        cursor = conn.execute("SELECT COUNT(*) as count FROM products")
        stats['total_products'] = cursor.fetchone()['count']
        
        # User count
        cursor = conn.execute("SELECT COUNT(*) as count FROM users")
        stats['total_users'] = cursor.fetchone()['count']
        
        # Order count
        cursor = conn.execute("SELECT COUNT(*) as count FROM orders")
        stats['total_orders'] = cursor.fetchone()['count']
        
        # Category count
        cursor = conn.execute("SELECT COUNT(DISTINCT category_name) as count FROM products")
        stats['total_categories'] = cursor.fetchone()['count']
        
        # Average price
        cursor = conn.execute("SELECT AVG(price) as avg_price FROM products")
        stats['average_price'] = round(cursor.fetchone()['avg_price'], 2)
        
        # Top categories
        cursor = conn.execute("""
            SELECT category_name, COUNT(*) as count 
            FROM products 
            GROUP BY category_name 
            ORDER BY count DESC 
            LIMIT 5
        """)
        stats['top_categories'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({'stats': stats})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Handle missing favicon and placeholder images
@app.route('/favicon.ico')
def favicon():
    return redirect('https://picsum.photos/32/32?random=favicon', code=302)

@app.route('/api/placeholder/<int:width>/<int:height>')
def placeholder_image(width, height):
    """Redirect to placeholder image service"""
    seed = request.args.get('seed', random.randint(1, 1000))
    return redirect(f'https://picsum.photos/{width}/{height}?random={seed}', code=302)

if __name__ == '__main__':
    print("🚀 Starting Enhanced E-commerce Backend with Real Olist Data...")
    print("✅ Backend is ready!")
    print("🌐 Starting server on http://localhost:5001")
    print("📊 API endpoints:")
    print("   - GET /api/health - Health check with database stats")
    print("   - GET /api/products - Get products with filtering")
    print("   - GET /api/products/<id> - Get single product")
    print("   - GET /api/products/<id>/recommendations - Product recommendations")
    print("   - GET /api/recommendations - Personalized recommendations")
    print("   - GET /api/categories - Get categories")
    print("   - GET /api/search - Advanced search")
    print("   - GET /api/stats - Database statistics")
    print("🇧🇷 Using Brazilian E-commerce (Olist) Dataset")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
