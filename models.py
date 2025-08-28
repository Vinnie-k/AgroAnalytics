from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model for Kenyan farmers with agriculture-specific fields"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    # Ensure password hash field has length of at least 256
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Farmer-specific information for Kenya
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    county = db.Column(db.String(50), nullable=False)  # Kenyan county
    sub_county = db.Column(db.String(50))
    ward = db.Column(db.String(50))
    farm_size = db.Column(db.Float)  # Farm size in acres
    farm_type = db.Column(db.String(50))  # e.g., 'Smallholder', 'Commercial'
    primary_crops = db.Column(db.Text)  # JSON string of crops grown
    farming_experience = db.Column(db.Integer)  # Years of experience
    is_admin = db.Column(db.Boolean, default=False)  # Admin flag
    subscription_status = db.Column(db.String(20), default='none')  # none, active, cancelled
    subscription_plan = db.Column(db.String(20), default='none')  # none, basic, premium, enterprise
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reports = db.relationship('Report', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class AgriculturalData(db.Model):
    """Model for storing processed agricultural data from KilimoSTAT and KNBS"""
    id = db.Column(db.Integer, primary_key=True)
    data_source = db.Column(db.String(50), nullable=False)  # 'KilimoSTAT' or 'KNBS'
    data_type = db.Column(db.String(50), nullable=False)  # 'crop_production', 'market_prices', etc.
    county = db.Column(db.String(50))
    crop_name = db.Column(db.String(50))
    season = db.Column(db.String(20))  # 'Short_Rains', 'Long_Rains'
    year = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float)
    unit = db.Column(db.String(20))  # 'tonnes', 'KES', 'hectares'
    raw_data = db.Column(db.JSON)  # Store original data
    processed_data = db.Column(db.JSON)  # Store ML-processed data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AgriculturalData {self.data_type}: {self.crop_name} - {self.county}>'

class Report(db.Model):
    """Model for storing generated agricultural reports"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # 'crop_analysis', 'market_trends', etc.
    content = db.Column(db.Text, nullable=False)
    insights = db.Column(db.JSON)  # ML-generated insights
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Report {self.title}>'

class ChatHistory(db.Model):
    """Model for storing AI chatbot conversation history"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='chat_history')
    
    def __repr__(self):
        return f'<ChatHistory {self.user_id}: {self.timestamp}>'
