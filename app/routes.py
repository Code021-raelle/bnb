from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, ListingForm, SearchForm, BookingForm, ReviewForm, MessageForm, EditProfileForm
from app.models import User, Listing, Review, Message, Booking
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import secrets
import os

@app.route("/")
@app.route("/home")
def home():
    current_year = 2024
    listings = Listing.query.all()
    return render_template('home.html', listings=listings, current_year=current_year)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)

    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/listing/new", methods=['GET', 'POST'])
@login_required
def new_listing():
    form = ListingForm()
    if form.validate_on_submit():
        if form.image.data:
            image_file = save_picture(form.image.data)
        else:
            image_file = 'default.jpg'
        
        listing = Listing(title=form.title.data, description=form.description.data, image_file=image_file, owner=current_user)
        db.session.add(listing)
        db.session.commit()
        flash('Your listing has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('listing.html', title='New Listing', form=form)


@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search_term = form.search.data
        min_price = form.min_price.data
        max_price = form.max_price.data
        location = form.location.data
        amenities = form.amenities.data.split(',') if form.amenities.data else []

        query = Listing.query.filter(Listing.title.contains(search_term) | Listing.description.contains(search_term))

        if min_price:
            query = query.filter(Listing.price >= min_price)
        if max_price:
            query = query.filter(Listing.price <= max_price)
        if location:
            query = query.filter(Listing.location.contains(location))
        if amenities:
            for amenity in amenities:
                query = query.filter(Listing.amenities.contains(amenity.strip()))

        listings = query.all()
        return render_template('search_results.html', listings=listings, search_term=search_term, form=form)
    return render_template('search.html', title='Search', form=form)


@app.route("/listing/<int:listing_id>/book", methods=['GET', 'POST'])
@login_required
def book_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    form = BookingForm()
    if form.validate_on_submit():
        booking = Booking(start_date=form.start_date.data, end_date=form.end_date.data, user=current_user, listing=listing)
        db.session.add(booking)
        db.session.commit()
        flash('Your booking has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('book_listing.html', title='Book Listing', form=form, listing=listing)


@app.route("/user/<string:username>")
def user_listings(username):
    user = User.query.filter_by(username=username).first_or_404()
    listings = Listing.query.filter_by(owner=user).all()
    bookings = Booking.query.filter_by(user=user).all()
    return render_template('user_listings.html', listings=listings, bookings=bookings, user=user)


@app.route("/send_message", methods=['GET', 'POST'])
@login_required
def send_message():
    form = MessageForm()
    if form.validate_on_submit():
        recipient = User.query.filter_by(username=form.recipient.data).first()
        if recipient:
            message = Message(body=form.body.data, sender=current_user, recipient=recipient)
            db.session.add(message)
            db.session.commit()
            flash('Your message has been sent!', 'success')
            return redirect(url_for('inbox'))
        else:
            flash('Recipient not found.', 'danger')
    return render_template('send_message.html', title='Send Message', form=form)

@app.route("/inbox", methods=['GET'])
@login_required
def inbox():
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
    return render_template('inbox.html', title='Inbox', messages=messages)


@app.route("/profile/<username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', title=f'{user.username}\'s Profile', user=user)

@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route("/listings")
def listings():
    page = request.args.get('page', 1, type=int)
    listings = Listing.query.paginate(page=page, per_page=10)
    return render_template('listings.html', listings=listings)

@app.route("/listing/<int:listing_id>", methods=['GET', 'POST'])
def listing(listing_id):
    user = current_user
    listing = Listing.query.get_or_404(listing_id)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            rating=form.rating.data,
            comment=form.comment.data,
            listing_id=listing.id,
            user_id = current_user.id
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('listing', listing_id=listing.id))
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(listing_id=listing.id).order_by(Review.timestamp.desc()).paginate(page=page, per_page=5)
    return render_template('listing.html', title=listing.title, listing=listing, form=form, reviews=reviews, user=user)


@app.route('/checkout/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def checkout(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if request.method == 'POST':
        try:
            charge = stripe.Charge.create(
                amount=int(listing.price * 100),  # Stripe amounts are in cents
                currency='usd',
                description=listing.title,
                source=request.form['stripeToken']
            )
            flash('Payment successful!', 'success')
            return redirect(url_for('listing', listing_id=listing.id))
        except stripe.error.StripeError:
            flash('Payment failed. Please try again.', 'danger')
    return render_template('checkout.html', listing=listing, stripe_public_key=app.config['STRIPE_PUBLIC_KEY'])
