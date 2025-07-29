import React, { useState } from 'react';
import ProductCard from '../components/ProductCard';

const Products = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Mock product data
  const allProducts = [
    {
      id: 1,
      name: "Wireless Bluetooth Headphones",
      price: 89.99,
      rating: 4.5,
      category: "electronics",
      image: "/api/placeholder/280/200"
    },
    {
      id: 2,
      name: "Smart Fitness Watch",
      price: 249.99,
      rating: 4.7,
      category: "electronics",
      image: "/api/placeholder/280/200"
    },
    {
      id: 3,
      name: "Portable Phone Charger",
      price: 29.99,
      rating: 4.3,
      category: "electronics",
      image: "/api/placeholder/280/200"
    },
    {
      id: 4,
      name: "Coffee Maker Pro",
      price: 129.99,
      rating: 4.6,
      category: "home",
      image: "/api/placeholder/280/200"
    },
    {
      id: 5,
      name: "Laptop Stand Adjustable",
      price: 59.99,
      rating: 4.4,
      category: "office",
      image: "/api/placeholder/280/200"
    },
    {
      id: 6,
      name: "Wireless Mouse",
      price: 34.99,
      rating: 4.2,
      category: "electronics",
      image: "/api/placeholder/280/200"
    },
    {
      id: 7,
      name: "USB-C Hub",
      price: 79.99,
      rating: 4.5,
      category: "electronics",
      image: "/api/placeholder/280/200"
    },
    {
      id: 8,
      name: "Ergonomic Office Chair",
      price: 299.99,
      rating: 4.8,
      category: "office",
      image: "/api/placeholder/280/200"
    },
    {
      id: 9,
      name: "LED Desk Lamp",
      price: 45.99,
      rating: 4.3,
      category: "office",
      image: "/api/placeholder/280/200"
    },
    {
      id: 10,
      name: "Air Purifier",
      price: 189.99,
      rating: 4.6,
      category: "home",
      image: "/api/placeholder/280/200"
    }
  ];

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'electronics', label: 'Electronics' },
    { value: 'home', label: 'Home & Kitchen' },
    { value: 'office', label: 'Office' }
  ];

  // Filter products based on search and category
  const filteredProducts = allProducts.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
      <h1 className="section-title">All Products</h1>
      
      {/* Filters */}
      <div style={{ 
        display: 'flex', 
        gap: '1rem', 
        marginBottom: '2rem', 
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <input
          type="text"
          placeholder="Search products..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '5px',
            fontSize: '16px',
            flex: '1',
            minWidth: '200px'
          }}
        />
        
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={{
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '5px',
            fontSize: '16px',
            minWidth: '150px'
          }}
        >
          {categories.map(category => (
            <option key={category.value} value={category.value}>
              {category.label}
            </option>
          ))}
        </select>
      </div>

      {/* Results count */}
      <div style={{ marginBottom: '1rem', color: '#666' }}>
        Showing {filteredProducts.length} products
      </div>

      {/* Products Grid */}
      <div className="products-grid">
        {filteredProducts.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>

      {/* No results */}
      {filteredProducts.length === 0 && (
        <div style={{ 
          textAlign: 'center', 
          padding: '4rem 0', 
          color: '#666' 
        }}>
          <h3>No products found</h3>
          <p>Try adjusting your search or category filter.</p>
        </div>
      )}
    </div>
  );
};

export default Products;
