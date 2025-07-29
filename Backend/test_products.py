import requests

# Test the products API
resp = requests.get('http://localhost:5000/api/products')
data = resp.json()

print(f"Total products available: {data['total']}")
print(f"Sample products: {[p['name'] for p in data['products'][:5]]}")

# Test categories
cat_resp = requests.get('http://localhost:5000/api/categories')
categories = cat_resp.json()['categories']
print(f"Available categories: {categories}")
print(f"Number of categories: {len(categories)}")
