from datetime import datetime
from decimal import Decimal
from app import db, login_manager, bcrypt, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import Serializer
from sqlalchemy import event
from sqlalchemy.orm import relationship
from .utils import get_currency_symbol


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=True)
    last_name = db.Column(db.String(20), nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    about_me = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(225), nullable=False, default='default.jpg')
    password = db.Column(db.String(255), nullable=False)
    oauth_provider = db.Column(db.String(50), nullable=True)
    oauth_provider_user_id = db.Column(db.String(255), nullable=True)
    listings = db.relationship('Listing', backref='owner', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    message_sent = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    message_received = db.relationship('Message', backref='recipient', lazy=True, foreign_keys='Message.recipient_id')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    preferred_currency = db.Column(db.String(10), default='USD')
    #last_message_read_time = db.Column(db.DateTime, default=datetime.utcnow)
    #is_active = db.Column(db.Boolean, default=True)
    #is_deleted = db.Column(db.Boolean, default=False)
    #is_banned = db.Column(db.Boolean, default=False)
    #is_suspended = db.Column(db.Boolean, default=False)
    #is_verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_keY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


# Event listener to automatically set the full_name before saving the user
@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def receive_before_insert(mapper, connection, target):
    target.full_name = f'{target.first_name} {target.last_name or ""}'

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    price = db.Column(db.Numeric, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    location = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Listing('{self.title}', '{self.date_posted}')"

    def format_price(self):
        symbol = get_currency_symbol(self.currency)
        return f"{symbol}{self.price:,.2f}"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    date_booked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    listing = db.relationship('Listing', backref=db.backref('bookings', lazy=True))
    user = relationship('User', backref='bookings')

    def __repr__(self):
        return f"<Booking {self.start_date} to {self.end_date} for listing {self.listing_id}>"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)

    user = db.relationship('User', backref='reviews')

    def __repr__(self):
        return f'<Review {self.rating} - {self.comment}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(200), nullable=True)

    

    def __repr__(self):
        return f'<Message {self.body}>'


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def get_currency_symbol(currency_code):
    currency_symbols = {
        'USD': '$',
        'NGN': '₦',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'AUD': '$',
        'CAD': '$',
        'CHF': 'CHF',
        'CNY': '¥',
        'HKD': '$',
        'NZD': '$',
        'SEK': 'kr',
        'SGD': '$',
        'ZAR': 'R'
    }
    return currency_symbols.get(currency_code, currency_code)
