import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './ProductDetail.css';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [product, setProduct] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    fetchProduct();
    fetchRecommendations(); // Content-based recommendations don't require authentication
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/products/${id}`);
      setProduct(response.data);
    } catch (error) {
      console.error('Error fetching product:', error);
      if (error.response?.status === 404) {
        setMessage('Product not found');
      } else {
        setMessage('Error loading product');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/products/${id}/recommendations`);
      setRecommendations(response.data.recommendations || []);
    } catch (error) {
      console.error('Error fetching product recommendations:', error);
    }
  };

  const addToCart = async () => {
    if (!isAuthenticated) {
      setMessage('Please login to add items to cart');
      return;
    }

    try {
      await axios.post('http://localhost:5000/api/cart', {
        product_id: parseInt(id),
        quantity: quantity
      });
      setMessage(`${quantity} item(s) added to cart!`);
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error adding to cart: ' + (error.response?.data?.message || 'Unknown error'));
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const addToWishlist = async () => {
    if (!isAuthenticated) {
      setMessage('Please login to add items to wishlist');
      return;
    }

    try {
      await axios.post('http://localhost:5000/api/wishlist', {
        product_id: parseInt(id)
      });
      setMessage('Product added to wishlist!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error adding to wishlist: ' + (error.response?.data?.message || 'Unknown error'));
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const RecommendationCard = ({ product }) => (
    <div className="recommendation-card" onClick={() => navigate(`/products/${product.id}`)}>
      <div className="rec-image">
        <span className="rec-placeholder">📦</span>
      </div>
      <div className="rec-info">
        <h4>{product.name}</h4>
        <p className="rec-price">${product.price?.toFixed(2)}</p>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="product-detail-container">
        <div className="loading">Loading product details...</div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="product-detail-container">
        <div className="error-state">
          <h2>Product Not Found</h2>
          <p>The product you're looking for doesn't exist.</p>
          <button onClick={() => navigate('/products')} className="btn btn-primary">
            Back to Products
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="product-detail-container">
      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      <div className="product-detail">
        <div className="product-image-large">
          <span className="product-placeholder-large">📦</span>
        </div>

        <div className="product-details">
          <nav className="breadcrumb">
            <span onClick={() => navigate('/products')} className="breadcrumb-link">
              Products
            </span>
            <span className="breadcrumb-separator">&gt;</span>
            <span className="breadcrumb-current">{product.name}</span>
          </nav>

          <h1 className="product-title">{product.name}</h1>
          <p className="product-category-tag">{product.category}</p>
          
          <div className="product-description-full">
            <p>{product.description}</p>
          </div>

          <div className="product-price-large">
            ${product.price?.toFixed(2)}
          </div>

          {isAuthenticated && (
            <div className="product-actions-detailed">
              <div className="quantity-selector">
                <label htmlFor="quantity">Quantity:</label>
                <select
                  id="quantity"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value))}
                  className="quantity-select"
                >
                  {[...Array(10)].map((_, i) => (
                    <option key={i + 1} value={i + 1}>{i + 1}</option>
                  ))}
                </select>
              </div>

              <div className="action-buttons">
                <button onClick={addToCart} className="btn btn-primary btn-large">
                  Add to Cart
                </button>
                <button onClick={addToWishlist} className="btn btn-outline btn-large">
                  ♡ Add to Wishlist
                </button>
              </div>
            </div>
          )}

          {!isAuthenticated && (
            <div className="auth-prompt">
              <p>Please <span onClick={() => navigate('/login')} className="auth-link">login</span> to add items to cart or wishlist</p>
            </div>
          )}
        </div>
      </div>

      {recommendations.length > 0 && (
        <div className="recommendations-section">
          <h2>Recommended for You</h2>
          <div className="recommendations-grid">
            {recommendations.slice(0, 4).map(rec => (
              <RecommendationCard key={rec.id} product={rec} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetail;
