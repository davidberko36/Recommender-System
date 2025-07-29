#!/usr/bin/env python3
"""
Simple startup script for the Flask backend
"""
import os
import sys
import sqlite3
import subprocess

def install_dependencies():
    """Install required dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def create_simple_app():
    """Create a simple Flask app without complex imports"""
    from flask import Flask, jsonify
    from flask_cors import CORS
    import sqlite3
    import pandas as pd
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Backend API is running!',
            'database': check_database()
        })
    
    @app.route('/api/products', methods=['GET'])
    def get_products():
        """Get sample products"""
        try:
            # Return sample products for now
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
                }
            ]
            
            return jsonify({
                'products': sample_products,
                'total': len(sample_products)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/recommendations', methods=['GET'])
    def get_recommendations():
        """Get sample recommendations"""
        sample_recommendations = [
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
            }
        ]
        
        return jsonify({'recommendations': sample_recommendations})
    
    def check_database():
        """Check if database exists and has data"""
        try:
            if os.path.exists('ecommerce.db'):
                return "Database file exists"
            else:
                return "Database not found"
        except Exception as e:
            return f"Database error: {str(e)}"
    
    return app

def main():
    """Main function to start the backend"""
    print("🚀 Starting E-commerce Backend...")
    
    # Install dependencies first
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Create and run the app
    app = create_simple_app()
    
    print("✅ Backend is ready!")
    print("🌐 Starting server on http://localhost:5000")
    print("📊 API endpoints:")
    print("   - GET /api/health - Health check")
    print("   - GET /api/products - Get products")
    print("   - GET /api/recommendations - Get recommendations")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
