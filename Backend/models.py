# This file will be imported after db is created in app.py
# Models will be defined as functions that take db as parameter

def create_models(db):
    """Create all database models"""
    
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.String(50), primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(128))
        customer_city = db.Column(db.String(100))
        customer_state = db.Column(db.String(2))
        customer_zip_code = db.Column(db.String(10))
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    class Product(db.Model):
        __tablename__ = 'products'
        
        id = db.Column(db.String(50), primary_key=True)
        category_name = db.Column(db.String(100))
        name_length = db.Column(db.Integer)
        description_length = db.Column(db.Integer)
        photos_qty = db.Column(db.Integer)
        weight_g = db.Column(db.Float)
        length_cm = db.Column(db.Float)
        height_cm = db.Column(db.Float)
        width_cm = db.Column(db.Float)
        
        # For frontend display
        name = db.Column(db.String(200))
        description = db.Column(db.Text)
        price = db.Column(db.Float)
        image_url = db.Column(db.String(500))
        rating = db.Column(db.Float, default=4.0)
        stock = db.Column(db.Integer, default=100)

    class Order(db.Model):
        __tablename__ = 'orders'
        
        id = db.Column(db.String(50), primary_key=True)
        customer_id = db.Column(db.String(50), nullable=False)
        order_status = db.Column(db.String(50))
        order_purchase_timestamp = db.Column(db.DateTime)
        order_approved_at = db.Column(db.DateTime)
        order_delivered_carrier_date = db.Column(db.DateTime)
        order_delivered_customer_date = db.Column(db.DateTime)
        order_estimated_delivery_date = db.Column(db.DateTime)
        total_amount = db.Column(db.Float)

    class OrderItem(db.Model):
        __tablename__ = 'order_items'
        
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        order_id = db.Column(db.String(50), nullable=False)
        product_id = db.Column(db.String(50), nullable=False)
        seller_id = db.Column(db.String(50))
        shipping_limit_date = db.Column(db.DateTime)
        price = db.Column(db.Float)
        freight_value = db.Column(db.Float)
        quantity = db.Column(db.Integer, default=1)

    class Payment(db.Model):
        __tablename__ = 'payments'
        
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        order_id = db.Column(db.String(50), nullable=False)
        payment_sequential = db.Column(db.Integer)
        payment_type = db.Column(db.String(50))
        payment_installments = db.Column(db.Integer)
        payment_value = db.Column(db.Float)

    class Review(db.Model):
        __tablename__ = 'reviews'
        
        id = db.Column(db.String(50), primary_key=True)
        order_id = db.Column(db.String(50))
        product_id = db.Column(db.String(50), nullable=False)
        review_score = db.Column(db.Integer)
        review_comment_title = db.Column(db.String(200))
        review_comment_message = db.Column(db.Text)
        review_creation_date = db.Column(db.DateTime)
        review_answer_timestamp = db.Column(db.DateTime)

    class Seller(db.Model):
        __tablename__ = 'sellers'
        
        id = db.Column(db.String(50), primary_key=True)
        seller_zip_code = db.Column(db.String(10))
        seller_city = db.Column(db.String(100))
        seller_state = db.Column(db.String(2))

    class CartItem(db.Model):
        __tablename__ = 'cart_items'
        
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        user_id = db.Column(db.String(50), nullable=False)
        product_id = db.Column(db.String(50), nullable=False)
        quantity = db.Column(db.Integer, default=1)
        added_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    return {
        'User': User,
        'Product': Product,
        'Order': Order,
        'OrderItem': OrderItem,
        'Payment': Payment,
        'Review': Review,
        'Seller': Seller,
        'CartItem': CartItem
    }
