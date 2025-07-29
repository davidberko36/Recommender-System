import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './Orders.css';

const Orders = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchOrders();
  }, [isAuthenticated, navigate]);

  const fetchOrders = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/orders');
      setOrders(response.data.orders || []);
    } catch (error) {
      console.error('Error fetching orders:', error);
      setMessage('Error loading orders');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return '#f39c12';
      case 'processing':
        return '#3498db';
      case 'shipped':
        return '#9b59b6';
      case 'delivered':
        return '#27ae60';
      case 'cancelled':
        return '#e74c3c';
      default:
        return '#7f8c8d';
    }
  };

  const OrderCard = ({ order }) => (
    <div className="order-card">
      <div className="order-header">
        <div className="order-info">
          <h3 className="order-id">Order #{order.id}</h3>
          <p className="order-date">{formatDate(order.created_at)}</p>
        </div>
        <div className="order-status">
          <span 
            className="status-badge"
            style={{ backgroundColor: getStatusColor(order.status) }}
          >
            {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
          </span>
        </div>
      </div>

      <div className="order-items">
        {order.items.map(item => (
          <div key={item.id} className="order-item">
            <div className="item-image">
              <span className="item-placeholder">📦</span>
            </div>
            <div className="item-details">
              <h4 className="item-name">{item.product.name}</h4>
              <p className="item-category">{item.product.category}</p>
              <div className="item-pricing">
                <span className="item-quantity">Qty: {item.quantity}</span>
                <span className="item-price">${item.price.toFixed(2)} each</span>
              </div>
            </div>
            <div className="item-total">
              ${(item.price * item.quantity).toFixed(2)}
            </div>
          </div>
        ))}
      </div>

      <div className="order-footer">
        <div className="order-total">
          <span className="total-label">Total: </span>
          <span className="total-amount">${order.total_amount.toFixed(2)}</span>
        </div>
        <div className="order-actions">
          {order.items.map(item => (
            <Link 
              key={item.id}
              to={`/products/${item.product.id}`}
              className="btn btn-outline btn-small"
            >
              View Product
            </Link>
          ))}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="orders-container">
        <div className="loading">Loading orders...</div>
      </div>
    );
  }

  return (
    <div className="orders-container">
      <div className="orders-header">
        <h1>My Orders</h1>
        
        {message && (
          <div className="message error">
            {message}
          </div>
        )}
      </div>

      {orders.length === 0 ? (
        <div className="empty-orders">
          <div className="empty-icon">📋</div>
          <h2>No orders yet</h2>
          <p>Your order history will appear here once you make your first purchase.</p>
          <button 
            onClick={() => navigate('/products')}
            className="btn btn-primary"
          >
            Start Shopping
          </button>
        </div>
      ) : (
        <>
          <div className="orders-stats">
            <div className="stat-item">
              <span className="stat-number">{orders.length}</span>
              <span className="stat-label">Total Orders</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">
                ${orders.reduce((sum, order) => sum + order.total_amount, 0).toFixed(2)}
              </span>
              <span className="stat-label">Total Spent</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">
                {orders.reduce((sum, order) => sum + order.items.length, 0)}
              </span>
              <span className="stat-label">Items Ordered</span>
            </div>
          </div>
          
          <div className="orders-list">
            {orders.map(order => (
              <OrderCard key={order.id} order={order} />
            ))}
          </div>
          
          <div className="orders-footer">
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

export default Orders;
