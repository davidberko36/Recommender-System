# ShopSmart - E-commerce Frontend

A modern React-based frontend for the recommender system e-commerce platform.

## Features

- **Modern UI/UX**: Clean, responsive design with mobile-first approach
- **Product Catalog**: Browse products with search and filtering
- **Product Details**: Detailed product pages with specifications
- **Recommendations**: AI-powered product recommendations (placeholders for now)
- **Shopping Cart**: Add, remove, and manage cart items
- **Responsive Design**: Works on desktop, tablet, and mobile

## Pages

- **Home**: Hero section with featured and recommended products
- **Products**: Product catalog with search and category filtering
- **Product Detail**: Individual product page with specifications and recommendations
- **Cart**: Shopping cart with quantity management and order summary

## Components

- **Header**: Navigation with logo, menu, and cart icon
- **Footer**: Site footer with copyright information
- **ProductCard**: Reusable product display component

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## API Integration

The frontend is configured to work with a Flask backend running on `http://localhost:5000`. 

Current implementation uses mock data, but can be easily connected to real APIs by:
- Replacing mock data with API calls using axios
- Updating the API endpoints in the components
- Adding state management for cart, user authentication, etc.

## Future Enhancements

- User authentication and profiles
- Real-time cart updates
- Payment integration
- Advanced filtering and sorting
- Product reviews and ratings
- Wishlist functionality
- Real-time recommendations from ML backend

## Tech Stack

- React 18
- React Router for navigation
- Axios for API calls
- Responsive CSS with Flexbox/Grid
- Modern ES6+ JavaScript
