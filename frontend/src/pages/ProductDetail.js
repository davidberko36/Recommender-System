import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ProductCard from '../components/ProductCard';

const ProductDetail = () => {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProduct();
    fetchRecommendations();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/products/${id}`);
      if (response.ok) {
        const productData = await response.json();
        setProduct(productData);
      } else {
        setError('Product not found');
      }
    } catch (err) {
      setError('Failed to load product');
      console.error('Error fetching product:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/products/${id}/recommendations`);
      if (response.ok) {
        const data = await response.json();
        setRecommendedProducts(data.recommendations || []);
      }
    } catch (err) {
      console.error('Error fetching recommendations:', err);
    }
  };

  const addToCart = () => {
    alert(`Added ${product.name} to cart!`);
  };

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: '2rem', textAlign: 'center' }}>
        <div style={{ 
          display: 'inline-block',
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #007bff',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          marginBottom: '1rem'
        }}></div>
        <p>Loading product...</p>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="container" style={{ paddingTop: '2rem', textAlign: 'center' }}>
        <h2>Product Not Found</h2>
        <p>{error || 'The product you are looking for does not exist.'}</p>
      </div>
    );
  }

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
      {/* Product Details */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '3rem', 
        marginBottom: '4rem' 
      }}>
        {/* Product Image */}
        <div>
          <img 
            src={product.image_url || "/api/placeholder/400/300"} 
            alt={product.name}
            style={{
              width: '100%',
              borderRadius: '8px',
              boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
            }}
          />
        </div>

        {/* Product Info */}
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>{product.name}</h1>
          
          <div style={{ 
            fontSize: '1.5rem', 
            fontWeight: 'bold', 
            color: '#007bff', 
            marginBottom: '1rem' 
          }}>
            ${product.price}
          </div>

          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.5rem', 
            marginBottom: '2rem' 
          }}>
            <span style={{ color: '#ffc107', fontSize: '1.2rem' }}>
              {'⭐'.repeat(Math.floor(product.rating))}
            </span>
            <span>({product.rating}) • Stock: {product.stock}</span>
          </div>

          <p style={{ 
            fontSize: '1.1rem', 
            lineHeight: '1.6', 
            marginBottom: '2rem',
            color: '#666'
          }}>
            {product.description}
          </p>

          <div style={{ marginBottom: '2rem' }}>
            <span style={{ 
              display: 'inline-block',
              backgroundColor: '#e9ecef',
              padding: '0.5rem 1rem',
              borderRadius: '20px',
              fontSize: '0.9rem',
              color: '#495057'
            }}>
              Category: {product.category_name?.replace('_', ' ').toUpperCase()}
            </span>
          </div>

          {/* Product Specifications */}
          {product.weight_g && (
            <div style={{ marginBottom: '2rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Specifications</h3>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>
                {product.weight_g && <p>Weight: {product.weight_g}g</p>}
                {product.length_cm && product.width_cm && product.height_cm && (
                  <p>Dimensions: {product.length_cm} × {product.width_cm} × {product.height_cm} cm</p>
                )}
                {product.photos_qty && <p>Photos available: {product.photos_qty}</p>}
              </div>
            </div>
          )}

          {/* Add to Cart Button */}
          <button 
            onClick={addToCart}
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              padding: '1rem 2rem',
              borderRadius: '5px',
              fontSize: '1.1rem',
              cursor: 'pointer',
              transition: 'background-color 0.3s'
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#0056b3'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#007bff'}
          >
            Add to Cart
          </button>
        </div>
      </div>

      {/* Recommended Products */}
      {recommendedProducts.length > 0 && (
        <div>
          <h2 style={{ marginBottom: '2rem' }}>You Might Also Like</h2>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '2rem' 
          }}>
            {recommendedProducts.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      )}

      {/* CSS for loading spinner */}
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ProductDetail;
