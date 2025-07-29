import React from 'react';

const Cart = () => {
  // Mock cart items
  const cartItems = [
    {
      id: 1,
      name: "Wireless Bluetooth Headphones",
      price: 89.99,
      quantity: 1,
      image: "/api/placeholder/100/100"
    },
    {
      id: 2,
      name: "Smart Fitness Watch",
      price: 249.99,
      quantity: 2,
      image: "/api/placeholder/100/100"
    }
  ];

  const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const shipping = 9.99;
  const tax = subtotal * 0.08; // 8% tax
  const total = subtotal + shipping + tax;

  const updateQuantity = (id, newQuantity) => {
    // In real app, update cart state
    console.log(`Update item ${id} to quantity ${newQuantity}`);
  };

  const removeItem = (id) => {
    // In real app, remove from cart state
    console.log(`Remove item ${id} from cart`);
  };

  if (cartItems.length === 0) {
    return (
      <div className="container" style={{ 
        paddingTop: '4rem', 
        paddingBottom: '4rem', 
        textAlign: 'center' 
      }}>
        <h1>Your Cart is Empty</h1>
        <p style={{ color: '#666', marginBottom: '2rem' }}>
          Add some products to get started!
        </p>
        <a href="/products" className="btn btn-primary" style={{ textDecoration: 'none' }}>
          Continue Shopping
        </a>
      </div>
    );
  }

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
      <h1 style={{ marginBottom: '2rem' }}>Shopping Cart</h1>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '2fr 1fr', 
        gap: '3rem' 
      }}>
        {/* Cart Items */}
        <div>
          {cartItems.map(item => (
            <div key={item.id} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              padding: '1.5rem',
              background: 'white',
              borderRadius: '8px',
              marginBottom: '1rem',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <img 
                src={item.image} 
                alt={item.name}
                style={{ 
                  width: '80px', 
                  height: '80px', 
                  objectFit: 'cover',
                  borderRadius: '4px'
                }}
              />
              
              <div style={{ flex: 1 }}>
                <h3 style={{ marginBottom: '0.5rem' }}>{item.name}</h3>
                <div style={{ 
                  fontSize: '1.1rem', 
                  fontWeight: 'bold', 
                  color: '#007bff' 
                }}>
                  ${item.price}
                </div>
              </div>

              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.5rem' 
              }}>
                <button 
                  onClick={() => updateQuantity(item.id, item.quantity - 1)}
                  style={{
                    width: '30px',
                    height: '30px',
                    border: '1px solid #ddd',
                    background: 'white',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  -
                </button>
                <span style={{ 
                  width: '40px', 
                  textAlign: 'center',
                  fontWeight: 'bold'
                }}>
                  {item.quantity}
                </span>
                <button 
                  onClick={() => updateQuantity(item.id, item.quantity + 1)}
                  style={{
                    width: '30px',
                    height: '30px',
                    border: '1px solid #ddd',
                    background: 'white',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  +
                </button>
              </div>

              <button 
                onClick={() => removeItem(item.id)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#dc3545',
                  fontSize: '1.2rem',
                  cursor: 'pointer',
                  padding: '0.5rem'
                }}
              >
                🗑️
              </button>
            </div>
          ))}
        </div>

        {/* Order Summary */}
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          height: 'fit-content'
        }}>
          <h2 style={{ marginBottom: '1.5rem' }}>Order Summary</h2>
          
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              marginBottom: '0.5rem'
            }}>
              <span>Subtotal:</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              marginBottom: '0.5rem'
            }}>
              <span>Shipping:</span>
              <span>${shipping.toFixed(2)}</span>
            </div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <span>Tax:</span>
              <span>${tax.toFixed(2)}</span>
            </div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              fontSize: '1.2rem',
              fontWeight: 'bold',
              paddingTop: '1rem',
              borderTop: '2px solid #eee'
            }}>
              <span>Total:</span>
              <span>${total.toFixed(2)}</span>
            </div>
          </div>

          <button 
            className="btn btn-primary" 
            style={{ width: '100%', marginBottom: '1rem' }}
          >
            Proceed to Checkout
          </button>
          
          <a 
            href="/products" 
            style={{ 
              display: 'block',
              textAlign: 'center',
              color: '#007bff',
              textDecoration: 'none'
            }}
          >
            Continue Shopping
          </a>
        </div>
      </div>
    </div>
  );
};

export default Cart;
