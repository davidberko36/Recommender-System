import React from 'react';
import { Link } from 'react-router-dom';

const ProductCard = ({ product }) => {
  return (
    <div className="product-card">
      <img 
        src={product.image || '/api/placeholder/280/200'} 
        alt={product.name}
        className="product-image"
      />
      <div className="product-info">
        <h3 className="product-title">{product.name}</h3>
        <div className="product-price">${product.price}</div>
        <div className="product-rating">
          <span className="stars">⭐⭐⭐⭐⭐</span>
          <span>({product.rating || '4.5'})</span>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link 
            to={`/products/${product.id}`} 
            className="btn btn-primary"
            style={{ flex: 1, textAlign: 'center', textDecoration: 'none' }}
          >
            View Details
          </Link>
          <button className="btn btn-secondary">
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
