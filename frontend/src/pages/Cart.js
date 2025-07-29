import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './Cart.css';

const Cart = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [placing, setPlacing] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchCart();
  }, [isAuthenticated, navigate]);

  const fetchCart = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/cart');
      setCartItems(response.data.cart_items || []);
    } catch (error) {
      console.error('Error fetching cart:', error);
      setMessage('Error loading cart items');
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId, newQuantity) => {
    if (newQuantity < 1) return;

    try {
      await axios.put('http://localhost:5000/api/cart', {
        item_id: itemId,
        quantity: newQuantity
      });
      
      setCartItems(cartItems.map(item => 
        item.id === itemId ? { ...item, quantity: newQuantity } : item
      ));
      setMessage('Cart updated successfully');
      setTimeout(() => setMessage(''), 2000);
    } catch (error) {
      setMessage('Error updating cart: ' + (error.response?.data?.message || 'Unknown error'));
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const removeItem = async (itemId) => {
    try {
      await axios.delete('http://localhost:5000/api/cart', {
        data: { item_id: itemId }
      });
      
      setCartItems(cartItems.filter(item => item.id !== itemId));
      setMessage('Item removed from cart');
      setTimeout(() => setMessage(''), 2000);
    } catch (error) {
      setMessage('Error removing item: ' + (error.response?.data?.message || 'Unknown error'));
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const placeOrder = async () => {
    if (cartItems.length === 0) {
      setMessage('Your cart is empty');
      return;
    }

    setPlacing(true);
    try {
      // eslint-disable-next-line no-unused-vars
      const response = await axios.post('http://localhost:5000/api/orders');
      setMessage('Order placed successfully!');
      setCartItems([]);
      setTimeout(() => {
        setMessage('');
        navigate('/orders');
      }, 2000);
    } catch (error) {
      setMessage('Error placing order: ' + (error.response?.data?.message || 'Unknown error'));
      setTimeout(() => setMessage(''), 3000);
    } finally {
      setPlacing(false);
    }
  };

  const getTotalPrice = () => {
    return cartItems.reduce((total, item) => total + (item.product.price * item.quantity), 0);
  };

  const CartItemCard = ({ item }) => (
    <div className="cart-item">
      <div className="item-image">
        <span className="item-placeholder">📦</span>
      </div>
      
      <div className="item-details">
        <h3 className="item-name">{item.product.name}</h3>
        <p className="item-category">{item.product.category}</p>
        <p className="item-price">${item.product.price?.toFixed(2)} each</p>
      </div>
      
      <div className="item-controls">
        <div className="quantity-controls">
          <button 
            onClick={() => updateQuantity(item.id, item.quantity - 1)}
            className="qty-btn"
            disabled={item.quantity <= 1}
          >
            -
          </button>
          <span className="quantity">{item.quantity}</span>
          <button 
            onClick={() => updateQuantity(item.id, item.quantity + 1)}
            className="qty-btn"
          >
            +
          </button>
        </div>
        
        <div className="item-total">
          ${(item.product.price * item.quantity).toFixed(2)}
        </div>
        
        <button 
          onClick={() => removeItem(item.id)}
          className="remove-btn"
        >
          Remove
        </button>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="cart-container">
        <div className="loading">Loading cart...</div>
      </div>
    );
  }

  return (
    <div className="cart-container">
      <div className="cart-header">
        <h1>Shopping Cart</h1>
        
        {message && (
          <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}
      </div>

      {cartItems.length === 0 ? (
        <div className="empty-cart">
          <div className="empty-icon">🛒</div>
          <h2>Your cart is empty</h2>
          <p>Add some products to get started!</p>
          <button 
            onClick={() => navigate('/products')}
            className="btn btn-primary"
          >
            Continue Shopping
          </button>
        </div>
      ) : (
        <>
          <div className="cart-items">
            {cartItems.map(item => (
              <CartItemCard key={item.id} item={item} />
            ))}
          </div>

          <div className="cart-summary">
            <div className="summary-content">
              <div className="summary-row">
                <span>Subtotal ({cartItems.length} items):</span>
                <span className="summary-price">${getTotalPrice().toFixed(2)}</span>
              </div>
              
              <div className="summary-actions">
                <button 
                  onClick={() => navigate('/products')}
                  className="btn btn-secondary"
                >
                  Continue Shopping
                </button>
                <button 
                  onClick={placeOrder}
                  className="btn btn-primary"
                  disabled={placing}
                >
                  {placing ? 'Placing Order...' : 'Place Order'}
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Cart;
