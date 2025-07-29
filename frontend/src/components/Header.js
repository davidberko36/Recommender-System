import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="header">
      <div className="container header-content">
        <Link to="/" className="logo">
          ShopSmart
        </Link>
        
        <nav>
          <ul className="nav-links">
            <li><Link to="/">Home</Link></li>
            <li><Link to="/products">Products</Link></li>
          </ul>
        </nav>
        
        <Link to="/cart" className="cart-icon">
          🛒
          <span className="cart-count">0</span>
        </Link>
      </div>
    </header>
  );
};

export default Header;
