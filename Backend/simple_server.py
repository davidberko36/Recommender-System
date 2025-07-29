from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Backend API is running!'
    })

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get sample products"""
    sample_products = [
        {
            'id': '1',
            'name': 'Premium Face Cream',
            'description': 'High-quality skincare product with excellent moisturizing properties.',
            'price': 49.99,
            'category_name': 'health_beauty',
            'image_url': 'https://picsum.photos/300/300?random=1',
            'rating': 4.5,
            'stock': 100
        },
        {
            'id': '2',
            'name': 'Wireless Bluetooth Headphones',
            'description': 'Premium audio experience with noise cancellation technology.',
            'price': 199.99,
            'category_name': 'electronics',
            'image_url': 'https://picsum.photos/300/300?random=2',
            'rating': 4.7,
            'stock': 50
        },
        {
            'id': '3',
            'name': 'Modern Coffee Table',
            'description': 'Stylish furniture piece perfect for modern living rooms.',
            'price': 299.99,
            'category_name': 'furniture_decor',
            'image_url': 'https://picsum.photos/300/300?random=3',
            'rating': 4.2,
            'stock': 25
        },
        {
            'id': '4',
            'name': 'Yoga Mat',
            'description': 'Non-slip exercise mat perfect for yoga and fitness.',
            'price': 39.99,
            'category_name': 'sports_leisure',
            'image_url': 'https://picsum.photos/300/300?random=4',
            'rating': 4.3,
            'stock': 75
        },
        {
            'id': '5',
            'name': 'Smart Phone Case',
            'description': 'Protective case with wireless charging compatibility.',
            'price': 24.99,
            'category_name': 'electronics',
            'image_url': 'https://picsum.photos/300/300?random=5',
            'rating': 4.1,
            'stock': 200
        },
        {
            'id': '6',
            'name': 'Organic Coffee Beans',
            'description': 'Premium organic coffee beans from sustainable farms.',
            'price': 19.99,
            'category_name': 'food_beverages',
            'image_url': 'https://picsum.photos/300/300?random=6',
            'rating': 4.6,
            'stock': 150
        }
    ]
    
    return jsonify({
        'products': sample_products,
        'total': len(sample_products)
    })

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product details"""
    # Sample product data
    products = {
        '1': {
            'id': '1',
            'name': 'Premium Face Cream',
            'description': 'High-quality skincare product with excellent moisturizing properties. Contains natural ingredients and vitamins for healthy skin.',
            'price': 49.99,
            'category_name': 'health_beauty',
            'image_url': 'https://picsum.photos/300/300?random=1',
            'rating': 4.5,
            'stock': 100
        },
        '2': {
            'id': '2',
            'name': 'Wireless Bluetooth Headphones',
            'description': 'Premium audio experience with noise cancellation technology. Perfect for music lovers and professionals.',
            'price': 199.99,
            'category_name': 'electronics',
            'image_url': 'https://picsum.photos/300/300?random=2',
            'rating': 4.7,
            'stock': 50
        }
    }
    
    if product_id in products:
        return jsonify(products[product_id])
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get sample recommendations"""
    sample_recommendations = [
        {
            'id': '7',
            'name': 'Vitamin C Serum',
            'description': 'Brightening serum with vitamin C for radiant skin.',
            'price': 29.99,
            'category_name': 'health_beauty',
            'image_url': 'https://picsum.photos/300/300?random=7',
            'rating': 4.4,
            'stock': 80
        },
        {
            'id': '8',
            'name': 'Wireless Charging Pad',
            'description': 'Fast wireless charging for compatible devices.',
            'price': 34.99,
            'category_name': 'electronics',
            'image_url': 'https://picsum.photos/300/300?random=8',
            'rating': 4.2,
            'stock': 120
        },
        {
            'id': '9',
            'name': 'Resistance Bands Set',
            'description': 'Complete resistance training set for home workouts.',
            'price': 24.99,
            'category_name': 'sports_leisure',
            'image_url': 'https://picsum.photos/300/300?random=9',
            'rating': 4.3,
            'stock': 90
        }
    ]
    
    return jsonify({'recommendations': sample_recommendations})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    categories = [
        {'category_name': 'health_beauty', 'count': 150},
        {'category_name': 'electronics', 'count': 89},
        {'category_name': 'furniture_decor', 'count': 65},
        {'category_name': 'sports_leisure', 'count': 78},
        {'category_name': 'food_beverages', 'count': 45},
        {'category_name': 'fashion_bags_accessories', 'count': 120}
    ]
    
    return jsonify({'categories': categories})

# Handle missing favicon and placeholder images
@app.route('/favicon.ico')
def favicon():
    return redirect('https://picsum.photos/32/32?random=favicon', code=302)

@app.route('/api/placeholder/<int:width>/<int:height>')
def placeholder_image(width, height):
    """Redirect to placeholder image service"""
    seed = request.args.get('seed', random.randint(1, 1000))
    return redirect(f'https://picsum.photos/{width}/{height}?random={seed}', code=302)

# Product recommendations for specific products
@app.route('/api/products/<product_id>/recommendations', methods=['GET'])
def get_product_recommendations(product_id):
    """Get recommendations for a specific product"""
    # Return sample recommendations based on product
    recommendations = [
        {
            'id': f'rec_{product_id}_1',
            'name': f'Related Product for {product_id}',
            'description': 'Similar product that customers also bought.',
            'price': round(random.uniform(15.99, 99.99), 2),
            'category_name': 'related',
            'image_url': f'https://picsum.photos/300/300?random=rec{product_id}1',
            'rating': round(random.uniform(4.0, 5.0), 1),
            'stock': random.randint(10, 100)
        },
        {
            'id': f'rec_{product_id}_2',
            'name': f'Complementary Item {product_id}',
            'description': 'Perfect complement to your selected product.',
            'price': round(random.uniform(20.99, 89.99), 2),
            'category_name': 'complementary',
            'image_url': f'https://picsum.photos/300/300?random=rec{product_id}2',
            'rating': round(random.uniform(4.0, 5.0), 1),
            'stock': random.randint(10, 100)
        }
    ]
    
    return jsonify({'recommendations': recommendations})

if __name__ == '__main__':
    print("🚀 Starting Simple E-commerce Backend...")
    print("✅ Backend is ready!")
    print("🌐 Starting server on http://localhost:5000")
    print("📊 API endpoints:")
    print("   - GET /api/health - Health check")
    print("   - GET /api/products - Get products")
    print("   - GET /api/products/<id> - Get single product")
    print("   - GET /api/recommendations - Get recommendations")
    print("   - GET /api/categories - Get categories")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
