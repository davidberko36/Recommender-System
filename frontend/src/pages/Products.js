import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './Products.css';

const Products = () => {
  const { isAuthenticated } = useAuth();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchProducts();
    fetchCategories();
  }, [selectedCategory, searchTerm]);

  const fetchProducts = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      if (searchTerm) params.append('search', searchTerm);
      
      const response = await axios.get(`http://localhost:5000/api/products?${params}`);
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('Error fetching products:', error);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/categories');
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const addToCart = async (productId) => {
    if (!isAuthenticated) {
      setMessage('Please login to add items to cart');
      return;
    }

    try {
      await axios.post('http://localhost:5000/api/cart', {
        product_id: productId,
        quantity: 1
      });
      setMessage('Product added to cart!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error adding to cart: ' + (error.response?.data?.message || 'Unknown error'));
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const addToWishlist = async (productId) => {
    if (!isAuthenticated) {
      setMessage('Please login to add items to wishlist');
      return;
    }

    try {
      await axios.post('http://localhost:5000/api/wishlist', {
        product_id: productId
      });
      setMessage('Product added to wishlist!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error adding to wishlist: ' + (error.response?.data?.message || 'Unknown error'));
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const ProductCard = ({ product }) => (
    <div className="product-card">
      <div className="product-image">
        <span className="product-placeholder">📦</span>
      </div>
      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-category">{product.category}</p>
        <p className="product-description">{product.description}</p>
        <p className="product-price">${product.price?.toFixed(2)}</p>
        
        <div className="product-actions">
          <Link to={`/products/${product.id}`} className="btn btn-primary">
            View Details
          </Link>
          {isAuthenticated && (
            <>
              <button 
                onClick={() => addToCart(product.id)}
                className="btn btn-success"
              >
                Add to Cart
              </button>
              <button 
                onClick={() => addToWishlist(product.id)}
                className="btn btn-outline"
              >
                ♡ Wishlist
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="products-container">
        <div className="loading">Loading products...</div>
      </div>
    );
  }

  return (
    <div className="products-container">
      <div className="products-header">
        <h1>Our Products</h1>
        
        {message && (
          <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}
        
        <div className="filters">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="category-filter">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="category-select"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {products.length === 0 ? (
        <div className="no-products">
          <p>No products found matching your criteria.</p>
        </div>
      ) : (
        <div className="products-grid">
          {products.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Products;
