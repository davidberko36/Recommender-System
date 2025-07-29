import React from 'react';
import { Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard';

const Home = () => {
  // Mock data for demonstration
  const featuredProducts = [
    {
      id: 1,
      name: "Wireless Bluetooth Headphones",
      price: 89.99,
      rating: 4.5,
      image: "/api/placeholder/280/200"
    },
    {
      id: 2,
      name: "Smart Fitness Watch",
      price: 249.99,
      rating: 4.7,
      image: "/api/placeholder/280/200"
    },
    {
      id: 3,
      name: "Portable Phone Charger",
      price: 29.99,
      rating: 4.3,
      image: "/api/placeholder/280/200"
    },
    {
      id: 4,
      name: "Coffee Maker Pro",
      price: 129.99,
      rating: 4.6,
      image: "/api/placeholder/280/200"
    }
  ];

  const recommendedProducts = [
    {
      id: 5,
      name: "Laptop Stand Adjustable",
      price: 59.99,
      rating: 4.4,
      image: "/api/placeholder/280/200"
    },
    {
      id: 6,
      name: "Wireless Mouse",
      price: 34.99,
      rating: 4.2,
      image: "/api/placeholder/280/200"
    },
    {
      id: 7,
      name: "USB-C Hub",
      price: 79.99,
      rating: 4.5,
      image: "/api/placeholder/280/200"
    }
  ];

  return (
    <div>
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1>Welcome to ShopSmart</h1>
          <p>Discover amazing products with AI-powered recommendations tailored just for you!</p>
          <Link to="/products" className="btn btn-primary" style={{ textDecoration: 'none' }}>
            Shop Now
          </Link>
        </div>
      </section>

      {/* Featured Products */}
      <section className="container" style={{ padding: '4rem 0' }}>
        <h2 className="section-title">Featured Products</h2>
        <div className="products-grid">
          {featuredProducts.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </section>

      {/* Recommended Products */}
      <section className="recommendations">
        <div className="container">
          <h2 className="section-title">Recommended for You</h2>
          <p style={{ textAlign: 'center', marginBottom: '2rem', color: '#666' }}>
            Based on your browsing history and preferences
          </p>
          <div className="products-grid">
            {recommendedProducts.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
