from datetime import datetime
from app import db, login_manager, bcrypt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=True)
    last_name = db.Column(db.String(20), nullable=True)
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


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Listing('{self.title}', '{self.date_posted}')"

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

    def __repr__(self):
        return f'<Message {self.body}>'
