import pandas as pd
import sqlite3
import numpy as np
from datetime import datetime
import random
import os

class DataLoader:
    def __init__(self, data_path='./olist'):
        self.data_path = data_path
        self.db_name = 'ecommerce.db'
        
    def load_olist_data(self):
        """Load and process Olist dataset"""
        print("Loading Olist dataset...")
        
        try:
            # Load all CSV files
            customers = pd.read_csv(f'{self.data_path}/olist_customers_dataset.csv')
            orders = pd.read_csv(f'{self.data_path}/olist_orders_dataset.csv')
            order_items = pd.read_csv(f'{self.data_path}/olist_order_items_dataset.csv')
            products = pd.read_csv(f'{self.data_path}/olist_products_dataset.csv')
            payments = pd.read_csv(f'{self.data_path}/olist_order_payments_dataset.csv')
            reviews = pd.read_csv(f'{self.data_path}/olist_order_reviews_dataset.csv')
            sellers = pd.read_csv(f'{self.data_path}/olist_sellers_dataset.csv')
            
            # Load category translation
            try:
                category_translation = pd.read_csv(f'{self.data_path}/product_category_name_translation.csv')
                # Create category mapping
                category_map = dict(zip(
                    category_translation['product_category_name'],
                    category_translation['product_category_name_english']
                ))
            except:
                category_map = {}
            
            print(f"Loaded {len(customers)} customers")
            print(f"Loaded {len(orders)} orders")
            print(f"Loaded {len(order_items)} order items")
            print(f"Loaded {len(products)} products")
            
            return {
                'customers': customers,
                'orders': orders,
                'order_items': order_items,
                'products': products,
                'payments': payments,
                'reviews': reviews,
                'sellers': sellers,
                'category_map': category_map
            }
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def process_products(self, products_df, category_map):
        """Process products data for our schema"""
        print("Processing products data...")
        
        # Create enhanced product data
        processed_products = []
        
        for _, product in products_df.iterrows():
            # Translate category name
            category_name = product.get('product_category_name', 'Unknown')
            if category_name in category_map:
                category_name = category_map[category_name]
            
            # Generate realistic product names and descriptions
            name = self.generate_product_name(category_name)
            description = self.generate_product_description(category_name)
            
            # Generate realistic prices based on category
            price = self.generate_price(category_name)
            
            # Generate image URL
            image_url = f"https://picsum.photos/300/300?random={hash(product['product_id']) % 1000}"
            
            processed_product = {
                'id': product['product_id'],
                'category_name': category_name,
                'name_length': product.get('product_name_lenght', 0),
                'description_length': product.get('product_description_lenght', 0),
                'photos_qty': product.get('product_photos_qty', 1),
                'weight_g': product.get('product_weight_g', 0),
                'length_cm': product.get('product_length_cm', 0),
                'height_cm': product.get('product_height_cm', 0),
                'width_cm': product.get('product_width_cm', 0),
                'name': name,
                'description': description,
                'price': price,
                'image_url': image_url,
                'rating': round(random.uniform(3.5, 5.0), 1),
                'stock': random.randint(10, 500)
            }
            
            processed_products.append(processed_product)
        
        return pd.DataFrame(processed_products)
    
    def generate_product_name(self, category):
        """Generate realistic product names based on category"""
        category_names = {
            'health_beauty': ['Premium Face Cream', 'Vitamin Supplement', 'Organic Shampoo', 'Anti-Aging Serum'],
            'computers_accessories': ['Wireless Mouse', 'USB Cable', 'Laptop Stand', 'Bluetooth Headphones'],
            'auto': ['Car Phone Mount', 'Tire Pressure Gauge', 'Car Charger', 'Steering Wheel Cover'],
            'furniture_decor': ['Modern Coffee Table', 'Decorative Pillow', 'Wall Art', 'Table Lamp'],
            'sports_leisure': ['Yoga Mat', 'Resistance Bands', 'Water Bottle', 'Fitness Tracker'],
            'toys': ['Educational Puzzle', 'Action Figure', 'Building Blocks', 'Board Game'],
            'fashion_bags_accessories': ['Leather Handbag', 'Stylish Watch', 'Designer Sunglasses', 'Fashion Scarf'],
            'housewares': ['Kitchen Utensils', 'Storage Container', 'Cutting Board', 'Coffee Mug'],
            'electronics': ['Smart Phone Case', 'Portable Charger', 'Bluetooth Speaker', 'Tablet Stand']
        }
        
        if category in category_names:
            return random.choice(category_names[category])
        else:
            return f"{category.replace('_', ' ').title()} Product"
    
    def generate_product_description(self, category):
        """Generate realistic product descriptions"""
        descriptions = [
            f"High-quality {category.replace('_', ' ')} product with excellent features and durability.",
            f"Premium {category.replace('_', ' ')} item designed for modern lifestyle and convenience.",
            f"Best-selling {category.replace('_', ' ')} product with outstanding customer reviews.",
            f"Professional-grade {category.replace('_', ' ')} item perfect for everyday use.",
        ]
        return random.choice(descriptions)
    
    def generate_price(self, category):
        """Generate realistic prices based on category"""
        price_ranges = {
            'health_beauty': (15, 150),
            'computers_accessories': (20, 300),
            'auto': (25, 200),
            'furniture_decor': (50, 500),
            'sports_leisure': (30, 250),
            'toys': (10, 80),
            'fashion_bags_accessories': (25, 300),
            'housewares': (15, 100),
            'electronics': (30, 400)
        }
        
        if category in price_ranges:
            min_price, max_price = price_ranges[category]
            return round(random.uniform(min_price, max_price), 2)
        else:
            return round(random.uniform(20, 200), 2)
    
    def save_to_database(self, data):
        """Save processed data to SQLite database"""
        print("Saving data to database...")
        
        conn = sqlite3.connect(self.db_name)
        
        try:
            # Save customers (as users)
            customers_df = data['customers'].copy()
            customers_df['id'] = customers_df['customer_id']
            customers_df['email'] = customers_df['customer_id'].apply(lambda x: f"user_{x[:8]}@example.com")
            customers_df['password_hash'] = 'default_hash'  # In real app, this would be properly hashed
            customers_df['created_at'] = datetime.now()
            
            customers_df[['id', 'email', 'password_hash', 'customer_city', 'customer_state', 
                         'customer_zip_code_prefix', 'created_at']].rename(columns={
                'customer_zip_code_prefix': 'customer_zip_code'
            }).to_sql('users', conn, if_exists='replace', index=False)
            
            # Save products
            processed_products = self.process_products(data['products'], data['category_map'])
            processed_products.to_sql('products', conn, if_exists='replace', index=False)
            
            # Save orders
            orders_df = data['orders'].copy()
            orders_df['total_amount'] = 0  # Will be calculated from order items
            orders_df.to_sql('orders', conn, if_exists='replace', index=False)
            
            # Save order items
            order_items_df = data['order_items'].copy()
            order_items_df['quantity'] = 1  # Assuming 1 quantity per item for simplicity
            order_items_df.to_sql('order_items', conn, if_exists='replace', index=False)
            
            # Save payments
            data['payments'].to_sql('payments', conn, if_exists='replace', index=False)
            
            # Save reviews
            data['reviews'].to_sql('reviews', conn, if_exists='replace', index=False)
            
            # Save sellers
            data['sellers'].to_sql('sellers', conn, if_exists='replace', index=False)
            
            # Update order totals
            self.update_order_totals(conn)
            
            print("Data saved successfully!")
            
        except Exception as e:
            print(f"Error saving data: {e}")
        finally:
            conn.close()
    
    def update_order_totals(self, conn):
        """Update order total amounts"""
        query = """
        UPDATE orders 
        SET total_amount = (
            SELECT SUM(price + freight_value) 
            FROM order_items 
            WHERE order_items.order_id = orders.id
        )
        """
        conn.execute(query)
        conn.commit()
    
    def load_and_process_all(self):
        """Main method to load and process all data"""
        print("Starting data loading process...")
        
        # Load raw data
        data = self.load_olist_data()
        if not data:
            print("Failed to load data")
            return False
        
        # Save to database
        self.save_to_database(data)
        
        print("Data loading completed successfully!")
        return True

if __name__ == "__main__":
    loader = DataLoader()
    loader.load_and_process_all()
