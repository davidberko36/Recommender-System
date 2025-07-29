#!/usr/bin/env python3
"""
Script to refresh the database with expanded product catalog
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from app import app, db, Product

def refresh_database():
    with app.app_context():
        print("Clearing existing products...")
        Product.query.delete()
        db.session.commit()
        
        print("Reinitializing with expanded product catalog...")
        from app import init_sample_data
        init_sample_data()
        
        print("Database refreshed successfully!")
        
        # Show stats
        total_products = Product.query.count()
        categories = db.session.query(Product.category).distinct().all()
        print(f"Total products: {total_products}")
        print(f"Categories: {[cat[0] for cat in categories]}")

if __name__ == "__main__":
    refresh_database()
