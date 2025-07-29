import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './Home.css';

const Home = () => {
  const { isAuthenticated } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [popularProducts, setPopularProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch popular products for all users
        const popularResponse = await axios.get('http://localhost:5000/api/products?limit=6');
        setPopularProducts(popularResponse.data.products || []);

        // Fetch recommendations for authenticated users
        if (isAuthenticated) {
          try {
            const recResponse = await axios.get('http://localhost:5000/api/recommendations?limit=6');
            console.log('Recommendations response:', recResponse.data);
            setRecommendations(recResponse.data.recommendations || []);
          } catch (recError) {
            console.error('Error fetching recommendations:', recError);
            console.log('Token exists:', !!localStorage.getItem('token'));
            // Fall back to popular products if recommendations fail
            setRecommendations([]);
          }
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated]);

  const ProductCard = ({ product }) => (
    <div className="product-card">
      <div className="product-image">
        <span className="product-placeholder">📦</span>
      </div>
      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-category">{product.category}</p>
        <p className="product-price">${product.price?.toFixed(2)}</p>
        <Link to={`/products/${product.id}`} className="view-product-btn">
          View Details
        </Link>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="home-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <section className="hero-section">
        <div className="hero-content">
          <h1>Welcome to RecommendMe</h1>
          <p>Discover products tailored just for you with our smart recommendation system</p>
          {!isAuthenticated && (
            <div className="hero-actions">
              <Link to="/register" className="cta-btn primary">Get Started</Link>
              <Link to="/products" className="cta-btn secondary">Browse Products</Link>
            </div>
          )}
        </div>
      </section>

      {isAuthenticated && recommendations.length > 0 && (
        <section className="section">
          <h2>Recommended for You</h2>
          <div className="products-grid">
            {recommendations.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
          <div className="section-footer">
            <Link to="/products" className="view-all-btn">View All Products</Link>
          </div>
        </section>
      )}

      <section className="section">
        <h2>Popular Products</h2>
        <div className="products-grid">
          {popularProducts.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
        <div className="section-footer">
          <Link to="/products" className="view-all-btn">View All Products</Link>
        </div>
      </section>

      <section className="features-section">
        <h2>Why Choose RecommendMe?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Smart Recommendations</h3>
            <p>Our AI-powered system learns your preferences to suggest products you'll love</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🛒</div>
            <h3>Easy Shopping</h3>
            <p>Simple cart and wishlist management for a seamless shopping experience</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📦</div>
            <h3>Order Tracking</h3>
            <p>Keep track of all your orders and purchase history in one place</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
