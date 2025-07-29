# E-Commerce Recommender System

A full-stack e-commerce application with AI-powered product recommendations built using Flask (Backend) and React (Frontend). The system implements hybrid recommendation algorithms using content-based filtering, collaborative filtering, and popularity-based recommendations with cosine similarity calculations.

## 🚀 Features

### Frontend (React)
- **User Authentication** - Secure registration and login system
- **Product Catalog** - Browse 49+ products across 9 categories
- **Shopping Cart** - Add, update, and remove items
- **Wishlist** - Save products for later
- **Order Management** - Place orders and view order history
- **Personalized Recommendations** - AI-powered product suggestions
- **Responsive Design** - Mobile-friendly interface

### Backend (Flask)
- **RESTful API** - Complete REST API with JWT authentication
- **Database Management** - SQLite database with SQLAlchemy ORM
- **Hybrid Recommender System** - Multiple recommendation algorithms
- **CORS Support** - Cross-origin resource sharing enabled
- **Product Management** - CRUD operations for products

### Recommender System
- **Content-Based Filtering** - Using TF-IDF vectorization and cosine similarity
- **Collaborative Filtering** - Item-based collaborative filtering with cosine similarity
- **Popularity-Based** - Fallback recommendations based on ratings and order frequency
- **Hybrid Approach** - Combines multiple algorithms for better accuracy

## 📁 Project Structure

```
Recommender-System/
├── Backend/                    # Flask API server
│   ├── app.py                 # Main Flask application
│   ├── instance/              # Database storage
│   │   └── ecommerce.db       # SQLite database
│   └── requirements.txt       # Python dependencies
├── Frontend/                   # React application
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   ├── pages/            # Page components
│   │   ├── context/          # React Context (Auth)
│   │   └── App.js            # Main React component
│   ├── public/               # Static assets
│   └── package.json          # Node.js dependencies
├── .venv/                    # Python virtual environment
└── README.md                 # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. **Navigate to project root and create virtual environment:**
   ```bash
   cd Recommender-System
   python -m venv .venv
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   cd Backend
   pip install -r requirements.txt
   ```

4. **Start the Flask server:**
   ```bash
   python app.py
   ```
   Server will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd Frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```
   Application will open on `http://localhost:3000`

## 🎯 Usage

1. **Open your browser** and go to `http://localhost:3000`
2. **Register a new account** or use the existing sample data
3. **Browse products** across 9 different categories
4. **Add items to cart** and **create wishlists**
5. **Place orders** to generate purchase history
6. **View personalized recommendations** on the home page

## 🤖 Recommender System Implementation

The system implements a **hybrid recommendation approach** combining three different algorithms:

### 1. Content-Based Filtering

**Algorithm:** TF-IDF Vectorization + Cosine Similarity

```python
def get_content_based_recommendations(product_id, limit=5):
    # Create content vectors from category + description
    products_df['content'] = (
        products_df['category'].fillna('') + ' ' + 
        products_df['description'].fillna('')
    )
    
    # TF-IDF Vectorization
    tfidf = TfidfVectorizer(max_features=100, stop_words='english')
    content_matrix = tfidf.fit_transform(products_df['content'])
    
    # Calculate cosine similarity
    content_sim = cosine_similarity(content_matrix[product_idx:product_idx+1], content_matrix)
    
    # Return top similar products
    similar_indices = content_sim.argsort()[::-1][1:limit+1]
```

**How it works:**
- Combines product category and description into a content string
- Converts text to numerical vectors using TF-IDF (Term Frequency-Inverse Document Frequency)
- Calculates cosine similarity between products
- Recommends products with highest similarity scores

**Use case:** "Users who viewed this product might also like..."

### 2. Collaborative Filtering

**Algorithm:** Item-Based Collaborative Filtering + Cosine Similarity

```python
def get_collaborative_recommendations(user_id, limit=10):
    # Create user-item interaction matrix
    user_item_matrix = interactions_df.pivot_table(
        index='user_id', 
        columns='product_id', 
        values='interactions', 
        fill_value=0
    )
    
    # Calculate item-item similarity matrix
    item_similarity = cosine_similarity(user_item_matrix.T)
    
    # Find recommendations based on user's purchase history
    for item in purchased_items:
        similar_items = item_similarity_df[item].sort_values(ascending=False)
        for similar_item, similarity in similar_items.head(20).items():
            if similarity > 0.1:  # Similarity threshold
                recommendations[similar_item] += similarity
```

**How it works:**
- Analyzes user purchase patterns to create interaction matrix
- Calculates similarity between items based on user behavior
- Recommends items similar to what the user has previously purchased
- Uses cosine similarity to measure item relationships

**Use case:** "Customers who bought this also bought..."

### 3. Popularity-Based Recommendations

**Algorithm:** Rating + Purchase Frequency Ranking

```python
def get_popular_products(limit=10):
    popular_df = pd.read_sql_query("""
        SELECT p.id, p.name, p.description, p.price, p.category, p.rating,
               COALESCE(order_counts.order_count, 0) as order_count
        FROM product p
        LEFT JOIN (
            SELECT oi.product_id, COUNT(*) as order_count
            FROM order_item oi
            GROUP BY oi.product_id
        ) order_counts ON p.id = order_counts.product_id
        ORDER BY p.rating DESC, order_counts.order_count DESC
    """)
```

**How it works:**
- Ranks products by rating and purchase frequency
- Serves as fallback when user has no purchase history
- Ensures new users get relevant recommendations

**Use case:** "Popular products" and "Trending now"

### 4. Hybrid Recommendation Strategy

The system intelligently combines all three approaches:

```python
@app.route('/api/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user):
    # Try collaborative filtering first (most personalized)
    collaborative_recs = get_collaborative_recommendations(current_user.id, limit)
    
    if collaborative_recs and len(collaborative_recs) > 0:
        return jsonify({'recommendations': collaborative_recs})
    else:
        # Fallback to popular products (for new users)
        popular_recs = get_popular_products(limit)
        return jsonify({'recommendations': popular_recs})
```

**Strategy:**
1. **Primary:** Collaborative filtering for users with purchase history
2. **Fallback:** Popular products for new users or when collaborative filtering fails
3. **Product-specific:** Content-based filtering on individual product pages

## 📊 Database Schema

### Core Tables
- **User** - User accounts and authentication
- **Product** - Product catalog (49 products across 9 categories)
- **CartItem** - Shopping cart items
- **WishlistItem** - User wishlists
- **Order** - Purchase orders
- **OrderItem** - Individual items in orders

### Categories Available
1. Electronics (7 products)
2. Home & Kitchen (6 products)
3. Sports & Fitness (6 products)
4. Books (6 products)
5. Clothing & Fashion (6 products)
6. Beauty & Personal Care (5 products)
7. Automotive (4 products)
8. Toys & Games (4 products)
9. Garden & Outdoor (5 products)

## 🔧 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login

### Products
- `GET /api/products` - Get all products (with pagination, filtering)
- `GET /api/products/<id>` - Get specific product
- `GET /api/categories` - Get all categories

### Recommendations
- `GET /api/recommendations` - Get personalized recommendations (authenticated)
- `GET /api/products/<id>/recommendations` - Get content-based recommendations

### Shopping
- `GET /api/cart` - Get cart items
- `POST /api/cart` - Add to cart
- `PUT /api/cart` - Update cart item
- `DELETE /api/cart` - Remove from cart

### Wishlist & Orders
- `GET /api/wishlist` - Get wishlist
- `POST /api/wishlist` - Add to wishlist
- `GET /api/orders` - Get order history
- `POST /api/orders` - Create new order

## 🧮 Mathematical Foundation

### Cosine Similarity Formula

The core of both content-based and collaborative filtering:

```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

Where:
- `A · B` is the dot product of vectors A and B
- `||A||` and `||B||` are the magnitudes of vectors A and B
- Result ranges from -1 to 1 (higher = more similar)

### TF-IDF Formula

For content-based filtering:

```
TF-IDF(t,d) = TF(t,d) × log(N / DF(t))
```

Where:
- `TF(t,d)` = Term frequency of term t in document d
- `N` = Total number of documents
- `DF(t)` = Number of documents containing term t

## 🚀 Future Enhancements

- [ ] **Deep Learning Models** - Neural collaborative filtering
- [ ] **Real-time Recommendations** - WebSocket-based live updates
- [ ] **A/B Testing** - Compare recommendation algorithm performance
- [ ] **User Feedback** - Explicit rating system for better recommendations
- [ ] **Cold Start Problem** - Better handling of new users/products
- [ ] **Scalability** - Redis caching and PostgreSQL migration
- [ ] **Analytics Dashboard** - Recommendation performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**David Berko**
- GitHub: [@davidberko36](https://github.com/davidberko36)

---

**Built with ❤️ using Flask, React, and Machine Learning**