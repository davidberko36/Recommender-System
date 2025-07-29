import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import sqlite3

class RecommenderSystem:
    def __init__(self, db):
        self.db = db
        self.user_item_matrix = None
        self.item_similarity_matrix = None
        self.product_features = None
        self.is_trained = False
        
    def load_data_from_db(self):
        """Load data from SQLite database for training"""
        try:
            # Get order items with product info
            query = """
            SELECT 
                oi.order_id,
                o.customer_id,
                oi.product_id,
                oi.price,
                p.category_name,
                r.review_score
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            LEFT JOIN reviews r ON r.order_id = oi.order_id AND r.product_id = oi.product_id
            """
            
            conn = sqlite3.connect('ecommerce.db')
            self.interactions_df = pd.read_sql_query(query, conn)
            
            # Get products for content-based recommendations
            products_query = """
            SELECT id, category_name, name, description, price, rating
            FROM products
            """
            self.products_df = pd.read_sql_query(products_query, conn)
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_user_item_matrix(self):
        """Create user-item interaction matrix"""
        if self.interactions_df is None or self.interactions_df.empty:
            return False
            
        try:
            # Create implicit feedback (1 for purchased, 0 for not purchased)
            user_item = self.interactions_df.groupby(['customer_id', 'product_id']).size().reset_index(name='interactions')
            
            # Pivot to create user-item matrix
            self.user_item_matrix = user_item.pivot(
                index='customer_id', 
                columns='product_id', 
                values='interactions'
            ).fillna(0)
            
            return True
        except Exception as e:
            print(f"Error creating user-item matrix: {e}")
            return False
    
    def calculate_item_similarity(self):
        """Calculate item-item similarity matrix using cosine similarity"""
        if self.user_item_matrix is None:
            return False
            
        try:
            # Transpose to get item-user matrix
            item_user_matrix = self.user_item_matrix.T
            
            # Calculate cosine similarity between items
            self.item_similarity_matrix = cosine_similarity(item_user_matrix)
            
            # Convert to DataFrame for easier handling
            self.item_similarity_df = pd.DataFrame(
                self.item_similarity_matrix,
                index=item_user_matrix.index,
                columns=item_user_matrix.index
            )
            
            return True
        except Exception as e:
            print(f"Error calculating item similarity: {e}")
            return False
    
    def train_content_based_features(self):
        """Train content-based features using product categories and descriptions"""
        if self.products_df is None or self.products_df.empty:
            return False
            
        try:
            # Combine category and description for content features
            self.products_df['content'] = (
                self.products_df['category_name'].fillna('') + ' ' +
                self.products_df['description'].fillna('')
            )
            
            # Create TF-IDF features
            tfidf = TfidfVectorizer(max_features=100, stop_words='english')
            self.content_features = tfidf.fit_transform(self.products_df['content'])
            
            return True
        except Exception as e:
            print(f"Error training content features: {e}")
            return False
    
    def train(self):
        """Train the recommender system"""
        print("Training recommender system...")
        
        # Load data
        if not self.load_data_from_db():
            print("Failed to load data from database")
            return False
        
        # Create user-item matrix
        if not self.create_user_item_matrix():
            print("Failed to create user-item matrix")
            return False
        
        # Calculate item similarity
        if not self.calculate_item_similarity():
            print("Failed to calculate item similarity")
            return False
        
        # Train content-based features
        if not self.train_content_based_features():
            print("Failed to train content features")
            return False
        
        self.is_trained = True
        print("Recommender system trained successfully!")
        return True
    
    def get_item_based_recommendations(self, user_id, num_recommendations=10):
        """Get item-based collaborative filtering recommendations"""
        if not self.is_trained or user_id not in self.user_item_matrix.index:
            return self.get_popular_products(num_recommendations)
        
        try:
            # Get user's purchased items
            user_items = self.user_item_matrix.loc[user_id]
            purchased_items = user_items[user_items > 0].index.tolist()
            
            # Calculate recommendations based on item similarity
            recommendations = defaultdict(float)
            
            for item in purchased_items:
                if item in self.item_similarity_df.index:
                    # Get similar items
                    similar_items = self.item_similarity_df[item].sort_values(ascending=False)
                    
                    for similar_item, similarity in similar_items.head(20).items():
                        if similar_item not in purchased_items and similarity > 0.1:
                            recommendations[similar_item] += similarity
            
            # Sort and return top recommendations
            sorted_recommendations = sorted(
                recommendations.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            recommended_product_ids = [item[0] for item in sorted_recommendations[:num_recommendations]]
            return self.get_product_details(recommended_product_ids)
            
        except Exception as e:
            print(f"Error getting item-based recommendations: {e}")
            return self.get_popular_products(num_recommendations)
    
    def get_content_based_recommendations(self, product_id, num_recommendations=5):
        """Get content-based recommendations for a specific product"""
        if not self.is_trained:
            return self.get_popular_products(num_recommendations)
        
        try:
            # Find product index
            product_idx = self.products_df[self.products_df['id'] == product_id].index
            if len(product_idx) == 0:
                return self.get_popular_products(num_recommendations)
            
            product_idx = product_idx[0]
            
            # Calculate content similarity
            content_sim = cosine_similarity(
                self.content_features[product_idx:product_idx+1],
                self.content_features
            ).flatten()
            
            # Get most similar products
            similar_indices = content_sim.argsort()[::-1][1:num_recommendations+1]
            recommended_product_ids = self.products_df.iloc[similar_indices]['id'].tolist()
            
            return self.get_product_details(recommended_product_ids)
            
        except Exception as e:
            print(f"Error getting content-based recommendations: {e}")
            return self.get_popular_products(num_recommendations)
    
    def get_popular_products(self, num_recommendations=10):
        """Fallback: Get popular products based on rating and interaction count"""
        try:
            conn = sqlite3.connect('ecommerce.db')
            query = """
            SELECT p.id, p.name, p.description, p.price, p.image_url, p.rating,
                   p.category_name, COUNT(oi.product_id) as purchase_count
            FROM products p
            LEFT JOIN order_items oi ON p.id = oi.product_id
            GROUP BY p.id
            ORDER BY p.rating DESC, purchase_count DESC
            LIMIT ?
            """
            
            result = pd.read_sql_query(query, conn, params=(num_recommendations,))
            conn.close()
            
            return result.to_dict('records')
            
        except Exception as e:
            print(f"Error getting popular products: {e}")
            return []
    
    def get_product_details(self, product_ids):
        """Get detailed product information"""
        if not product_ids:
            return []
        
        try:
            conn = sqlite3.connect('ecommerce.db')
            placeholders = ','.join(['?' for _ in product_ids])
            query = f"""
            SELECT id, name, description, price, image_url, rating, category_name
            FROM products
            WHERE id IN ({placeholders})
            """
            
            result = pd.read_sql_query(query, conn, params=product_ids)
            conn.close()
            
            return result.to_dict('records')
            
        except Exception as e:
            print(f"Error getting product details: {e}")
            return []
    
    def get_recommendations_for_user(self, user_id, num_recommendations=10):
        """Main method to get recommendations for a user"""
        if not self.is_trained:
            # Train the model if not already trained
            self.train()
        
        return self.get_item_based_recommendations(user_id, num_recommendations)
    
    def get_similar_products(self, product_id, num_recommendations=5):
        """Get similar products for a given product"""
        if not self.is_trained:
            self.train()
        
        return self.get_content_based_recommendations(product_id, num_recommendations)
