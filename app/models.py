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
    bookings = db.relationship('Booking', back_populates='user', lazy=True)
    phone_number = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    message_sent = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    message_received = db.relationship('Message', backref='recipient', lazy=True, foreign_keys='Message.recipient_id')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    preferred_currency = db.Column(db.String(10), default='USD')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
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
        s = Serializer(app.config['SECRET_KEY'])
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


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False, default='default.jpg')
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    listing = db.relationship('Listing', back_populates='images')


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    images = db.relationship('Image', back_populates='listing', cascade="all, delete-orphan")
    price = db.Column(db.Numeric, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    location = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    bookings = db.relationship('Booking', backref='listing_bookings', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='listings')
    amenities = db.relationship('ListingAmenity', back_populates='listing')

    @property
    def owner(self):
        return User.query.get(self.user_id)

    def __repr__(self):
        return f"Listing('{self.title}', '{self.date_posted}')"

    def format_price(self):
        symbol = get_currency_symbol(self.currency)
        return f"{symbol}{self.price:,.2f}"


class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    abbreviation = db.Column(db.String(2), nullable=False)
    listings = db.relationship('Listing', backref='state', lazy=True)

    def __repr__(self):
        return f'<State {self.name}>'
    

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    listings = db.relationship('ListingAmenity', back_populates='amenity')

    def __repr__(self):
        return f'<Amenity {self.name}>'


class ListingAmenity(db.Model):
    __tablename__ = 'listing_amenity'
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), primary_key=True)
    amenity_id = db.Column(db.Integer, db.ForeignKey('amenity.id'), primary_key=True)
    listing = db.relationship('Listing', back_populates='amenities')
    amenity = db.relationship('Amenity', back_populates='listings')

    def __repr__(self):
        return f'<ListingAmenity Listing: {self.listing_id}, Amenity: {self.amenity_id}>'


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], back_populates='bookings')
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    date_booked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    listings = db.relationship('Listing', backref='listing_bookings', lazy=True)
    user = db.relationship('User', foreign_keys=[user_id], back_populates='bookings')

    def __repr__(self):
        return f"<Booking {self.start_date} to {self.end_date} for listing {self.listing_id}>"
    

def is_available(self, start_date, end_date):
    overlapping_bookings = self.bookings.filter(
        db.or_(
            db.and_(Booking.start_date <= start_date, Booking.end_date >= start_date),
            db.and_(Booking.start_date <= end_date, Booking.end_date >= end_date),
            db.and_(start_date <= Booking.start_date, end_date >= Booking.end_date)
        )
    ).all()
    return len(overlapping_bookings) == 0


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
