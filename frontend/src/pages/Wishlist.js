import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './Wishlist.css';

const Wishlist = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchWishlist();
  }, [isAuthenticated, navigate]);

  const fetchWishlist = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/wishlist');
      setWishlistItems(response.data.wishlist_items || []);
    } catch (error) {
      console.error('Error fetching wishlist:', error);
      setMessage('Error loading wishlist items');
    } finally {
      setLoading(false);
    }
  };

  const removeFromWishlist = async (itemId) => {
    try {
      await axios.delete('http://localhost:5000/api/wishlist', {
        data: { item_id: itemId }
      });
      
      setWishlistItems(wishlistItems.filter(item => item.id !== itemId));
      setMessage('Item removed from wishlist');
      setTimeout(() => setMessage(''), 2000);
    } catch (error) {
      setMessage('Error removing item: ' + (error.response?.data?.message || 'Unknown error'));
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const addToCart = async (productId) => {
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

  const WishlistItemCard = ({ item }) => (
    <div className="wishlist-item">
      <div className="item-image">
        <span className="item-placeholder">📦</span>
      </div>
      
      <div className="item-details">
        <h3 className="item-name">{item.product.name}</h3>
        <p className="item-category">{item.product.category}</p>
        <p className="item-description">{item.product.description}</p>
        <p className="item-price">${item.product.price?.toFixed(2)}</p>
      </div>
      
      <div className="item-actions">
        <Link 
          to={`/products/${item.product.id}`}
          className="btn btn-primary"
        >
          View Details
        </Link>
        <button 
          onClick={() => addToCart(item.product.id)}
          className="btn btn-success"
        >
          Add to Cart
        </button>
        <button 
          onClick={() => removeFromWishlist(item.id)}
          className="btn btn-outline"
        >
          Remove
        </button>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="wishlist-container">
        <div className="loading">Loading wishlist...</div>
      </div>
    );
  }

  return (
    <div className="wishlist-container">
      <div className="wishlist-header">
        <h1>My Wishlist</h1>
        
        {message && (
          <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}
      </div>

      {wishlistItems.length === 0 ? (
        <div className="empty-wishlist">
          <div className="empty-icon">♡</div>
          <h2>Your wishlist is empty</h2>
          <p>Save items you love for later!</p>
          <button 
            onClick={() => navigate('/products')}
            className="btn btn-primary"
          >
            Browse Products
          </button>
        </div>
      ) : (
        <>
          <div className="wishlist-stats">
            <p>{wishlistItems.length} item{wishlistItems.length !== 1 ? 's' : ''} saved</p>
          </div>
          
          <div className="wishlist-items">
            {wishlistItems.map(item => (
              <WishlistItemCard key={item.id} item={item} />
            ))}
          </div>
          
          <div className="wishlist-footer">
            <button 
              onClick={() => navigate('/products')}
              className="btn btn-secondary"
            >
              Continue Shopping
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Wishlist;
