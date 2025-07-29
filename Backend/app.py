from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Create models
from models import create_models
models = create_models(db)

# Extract model classes for easier access
User = models['User']
Product = models['Product']
Order = models['Order']
OrderItem = models['OrderItem']
Payment = models['Payment']
Review = models['Review']
Seller = models['Seller']
CartItem = models['CartItem']

# Initialize recommender system
from recommender import RecommenderSystem
recommender = RecommenderSystem(db)

# Import routes (these need to be after model creation)
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
