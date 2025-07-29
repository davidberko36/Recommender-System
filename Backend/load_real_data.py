#!/usr/bin/env python3
"""
Real Data Loader for Olist Brazilian E-commerce Dataset
This script loads actual data from the Olist dataset into our backend
"""

import pandas as pd
import sqlite3
import random
import os
from datetime import datetime, timedelta

class OlistDataLoader:
    def __init__(self):
        self.data_path = './olist'
        self.db_name = 'ecommerce_real.db'
        
    def load_category_translation(self):
        """Load and create category translation mapping"""
        try:
            category_df = pd.read_csv(f'{self.data_path}/product_category_name_translation.csv')
            return dict(zip(category_df['product_category_name'], 
                          category_df['product_category_name_english']))
        except:
            return {}
    
    def generate_realistic_product_data(self, product_row, category_map):
        """Generate realistic product data from Olist product info"""
        category_pt = product_row.get('product_category_name', 'outros')
        
        # Handle NaN values
        if pd.isna(category_pt) or category_pt is None:
            category_pt = 'outros'
        
        category_en = category_map.get(category_pt, str(category_pt).replace('_', ' ').title())
        
        # Generate realistic names based on category
        product_names = {
            'health_beauty': ['Anti-Aging Cream', 'Vitamin Supplement', 'Moisturizing Lotion', 'Face Serum'],
            'computers_accessories': ['Wireless Mouse', 'USB Cable', 'Laptop Bag', 'Keyboard'],
            'auto': ['Car Charger', 'Phone Mount', 'Tire Gauge', 'Air Freshener'],
            'furniture_decor': ['Coffee Table', 'Wall Clock', 'Picture Frame', 'Decorative Lamp'],
            'sports_leisure': ['Yoga Mat', 'Water Bottle', 'Resistance Bands', 'Sports Watch'],
            'toys': ['Educational Puzzle', 'Building Blocks', 'Action Figure', 'Board Game'],
            'baby': ['Baby Bottle', 'Soft Toy', 'Baby Blanket', 'Pacifier'],
            'bed_bath_table': ['Towel Set', 'Bed Sheets', 'Pillow', 'Bathroom Mat'],
            'perfumery': ['Perfume', 'Body Spray', 'Essential Oil', 'Cologne'],
            'housewares': ['Kitchen Utensils', 'Storage Box', 'Cleaning Supplies', 'Organizer']
        }
        
        # Get name based on category
        if category_en in product_names:
            base_name = random.choice(product_names[category_en])
        else:
            base_name = f"{category_en.replace('_', ' ').title()} Product"
        
        # Add variation to name
        variations = ['Premium', 'Deluxe', 'Professional', 'Classic', 'Modern', 'Eco-Friendly']
        name = f"{random.choice(variations)} {base_name}"
        
        # Generate price based on category and weight
        weight = product_row.get('product_weight_g', 500)
        base_price = max(10, min(500, weight * 0.1 + random.uniform(5, 50)))
        
        # Category-based price adjustments
        category_multipliers = {
            'computers_accessories': 2.0,
            'auto': 1.5,
            'furniture_decor': 3.0,
            'perfumery': 1.8,
            'toys': 0.8,
            'baby': 1.2
        }
        
        price = base_price * category_multipliers.get(category_en, 1.0)
        price = round(price, 2)
        
        # Generate description
        description = f"High-quality {category_en.replace('_', ' ')} product. "
        if weight > 1000:
            description += "Durable and long-lasting. "
        if product_row.get('product_photos_qty', 1) > 2:
            description += "Multiple product views available. "
        description += f"Dimensions: {product_row.get('product_length_cm', 0)}x{product_row.get('product_width_cm', 0)}x{product_row.get('product_height_cm', 0)}cm"
        
        return {
            'id': product_row['product_id'],
            'name': name,
            'description': description,
            'price': price,
            'category_name': category_en,
            'image_url': f"https://picsum.photos/300/300?random={hash(product_row['product_id']) % 1000}",
            'rating': round(random.uniform(3.5, 5.0), 1),
            'stock': random.randint(5, 200),
            'weight_g': product_row.get('product_weight_g', 0),
            'length_cm': product_row.get('product_length_cm', 0),
            'height_cm': product_row.get('product_height_cm', 0),
            'width_cm': product_row.get('product_width_cm', 0),
            'photos_qty': product_row.get('product_photos_qty', 1)
        }
    
    def load_and_process_data(self):
        """Load and process Olist data"""
        print("🔄 Loading Olist Brazilian E-commerce Dataset...")
        
        # Load category translation
        category_map = self.load_category_translation()
        print(f"✅ Loaded {len(category_map)} category translations")
        
        # Load products (limit to 1000 for demo)
        print("📦 Loading products...")
        products_df = pd.read_csv(f'{self.data_path}/olist_products_dataset.csv').head(1000)
        print(f"✅ Loaded {len(products_df)} products")
        
        # Process products
        processed_products = []
        for _, product in products_df.iterrows():
            processed_product = self.generate_realistic_product_data(product, category_map)
            processed_products.append(processed_product)
        
        products_final_df = pd.DataFrame(processed_products)
        
        # Load orders (sample)
        print("📋 Loading orders...")
        orders_df = pd.read_csv(f'{self.data_path}/olist_orders_dataset.csv').head(500)
        
        # Load order items
        print("🛒 Loading order items...")
        order_items_df = pd.read_csv(f'{self.data_path}/olist_order_items_dataset.csv').head(1000)
        
        # Load customers
        print("👥 Loading customers...")
        customers_df = pd.read_csv(f'{self.data_path}/olist_customers_dataset.csv').head(300)
        
        return {
            'products': products_final_df,
            'orders': orders_df,
            'order_items': order_items_df,
            'customers': customers_df
        }
    
    def save_to_database(self, data):
        """Save processed data to SQLite database"""
        print("💾 Saving data to database...")
        
        conn = sqlite3.connect(self.db_name)
        
        try:
            # Save products
            data['products'].to_sql('products', conn, if_exists='replace', index=False)
            print(f"✅ Saved {len(data['products'])} products")
            
            # Process and save customers as users
            customers = data['customers'].copy()
            customers['id'] = customers['customer_id']
            customers['email'] = customers['customer_id'].apply(lambda x: f"user_{x[:8]}@example.com")
            customers['password_hash'] = 'demo_hash'
            customers['created_at'] = datetime.now()
            
            customers[['id', 'email', 'password_hash', 'customer_city', 'customer_state', 
                      'customer_zip_code_prefix', 'created_at']].rename(columns={
                'customer_zip_code_prefix': 'customer_zip_code'
            }).to_sql('users', conn, if_exists='replace', index=False)
            print(f"✅ Saved {len(customers)} users")
            
            # Save orders
            data['orders']['total_amount'] = 0  # Will calculate later
            data['orders'].to_sql('orders', conn, if_exists='replace', index=False)
            print(f"✅ Saved {len(data['orders'])} orders")
            
            # Save order items
            order_items = data['order_items'].copy()
            order_items['quantity'] = 1
            order_items.to_sql('order_items', conn, if_exists='replace', index=False)
            print(f"✅ Saved {len(order_items)} order items")
            
            print("🎉 Database created successfully!")
            
        except Exception as e:
            print(f"❌ Error saving data: {e}")
        finally:
            conn.close()
    
    def create_sample_api_data(self):
        """Create sample data for our API endpoints"""
        conn = sqlite3.connect(self.db_name)
        
        try:
            # Get random products for API
            products_query = """
            SELECT id, name, description, price, category_name, image_url, rating, stock
            FROM products 
            ORDER BY RANDOM() 
            LIMIT 20
            """
            products = pd.read_sql_query(products_query, conn)
            
            # Get categories
            categories_query = """
            SELECT category_name, COUNT(*) as count
            FROM products
            GROUP BY category_name
            ORDER BY count DESC
            """
            categories = pd.read_sql_query(categories_query, conn)
            
            return {
                'products': products.to_dict('records'),
                'categories': categories.to_dict('records')
            }
            
        except Exception as e:
            print(f"Error creating API data: {e}")
            return {'products': [], 'categories': []}
        finally:
            conn.close()
    
    def run_full_load(self):
        """Main method to run the full data loading process"""
        print("🚀 Starting Olist Data Loading Process...")
        print("=" * 50)
        
        # Load and process data
        data = self.load_and_process_data()
        
        # Save to database
        self.save_to_database(data)
        
        # Create sample API data
        api_data = self.create_sample_api_data()
        
        print("=" * 50)
        print("✅ Data loading completed successfully!")
        print(f"📊 Products loaded: {len(data['products'])}")
        print(f"👥 Users created: {len(data['customers'])}")
        print(f"📋 Orders processed: {len(data['orders'])}")
        print(f"🛒 Order items: {len(data['order_items'])}")
        print(f"🏷️ Categories: {len(api_data['categories'])}")
        
        return True

if __name__ == "__main__":
    loader = OlistDataLoader()
    loader.run_full_load()
