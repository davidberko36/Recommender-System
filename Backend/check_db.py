import sqlite3
import os

db_path = os.path.join('instance', 'ecommerce.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:", tables)

# Check if product table exists and has data
if 'product' in tables:
    cursor.execute("SELECT COUNT(*) FROM product;")
    product_count = cursor.fetchone()[0]
    print(f"Products in database: {product_count}")
    
    if product_count > 0:
        cursor.execute("SELECT id, name, price FROM product LIMIT 3;")
        sample_products = cursor.fetchall()
        print("Sample products:", sample_products)

conn.close()
