from flask import render_template, url_for, flash, redirect, request, jsonify, current_app, make_response, session
from app import app, db, bcrypt, oauth, socketio
from decimal import Decimal
from flask_socketio import SocketIO, emit
from app.forms import (RegistrationForm, LoginForm, ListingForm, SearchForm, BookingForm,
                        ReviewForm, MessageForm, EditProfileForm, PreferredCurrencyForm,
                        ResetPasswordForm, RequestResetForm, UpdateUserForm)
from app.models import User, Listing, Review, Message, Booking, Chat, State, Amenity, ListingAmenity, Image
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app.utils import send_reset_email
from PIL import Image as PILImage
from datetime import datetime, timedelta, date, time
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import requests
import secrets
import logging
import json
import os


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

logging.basicConfig(level=logging.DEBUG)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, time)):
            return obj.isoformat()
        elif isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        return super(CustomJSONEncoder, self).default(obj)


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_picture(files):
    filenames = []

    for file in files:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.root_path, 'static/images', filename)
            file.save(file_path)
            filenames.append(filename)

    return filenames


@app.route("/")
@app.route("/home")
def home():
    form = PreferredCurrencyForm()
    
    current_year = 2024
    listings = Listing.query.all()
    return render_template('home.html', listings=listings, current_year=current_year, form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        username = form.username.data
        email = form.email.data

        existing_username = User.query.filter_by(username=username).first()
        existing_user = User.query.filter_by(email=email).first()
        if existing_username:
            flash('Username is taken', 'danger')
        elif existing_user:
            flash('You have an account with us. Please login.', 'danger')
            return redirect(url_for('login'))
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(hashed_password)
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
            response = make_response(redirect(url_for('home')))
            # Sets a cookie for user currency preference
            response.set_cookie('preferred_currency', 'USD', max_age=60*60*24*30)
            flash('Logged in successfully.', 'success')
            return response
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/google_login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    user_info = resp.json()
    user = User.query.filter_by(email=user_info['emails'][0]['value']).first()
    if user is None:
        user = User(email=user_info['emails'][0]['value'], username=user_info['displayName'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('home'))


@app.route('/facebook_login')
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    resp = facebook.get('/me?fields=name,email')
    assert resp.ok, resp.text
    user_info = resp.json()
    user = User.query.filter_by(email=user_info['email']).first()
    if user is None:
        user = User(email=user_info['email'], username=user_info['name'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('home'))


@app.route('/apple_login')
def apple_login():
    redirect_uri = url_for('apple_authorize', _external=True)
    return oauth.apple.authorize_redirect(redirect_uri)


@app.route('/apple/authorize')
def apple_authorize():
    token = oauth.apple.authorize_access_token()
    resp = requests.get('https://appleid.apple.com/auth/verifyCredentials', headers={'Authorization': 'Bearer ' + token['access_token']})
    assert resp.ok, resp.text
    user_info = resp.json()
    user = User.query.filter_by(email=user_info['email']).first()
    if user is None:
        user = User(email=user_info['email'], username=user_info['name'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('home'))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/help-center")
def help():
    current_year = 2024
    return render_template('help-center.html', current_year=current_year)


@app.route("/terms-and-conditions")
def terms_and_conditions():
    current_year = 2024
    return render_template('terms_and_conditions.html', current_year=current_year)


@app.route("/privacy-&-policy")
def privacy_policy():
    current_year = 2024
    return render_template('privacy_policy.html', current_year=current_year)


@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    search_term = request.args.get('q', '')  # Default to an empty string if no query is provided
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    location = request.args.get('location')
    state = request.args.get('state')
    amenities = request.args.get('amenities', '').split(',') if request.args.get('amenities') else []

    query = Listing.query.filter(Listing.title.contains(search_term) | Listing.description.contains(search_term))

    if min_price:
        query = query.filter(Listing.price >= float(min_price))
    if max_price:
        query = query.filter(Listing.price <= float(max_price))
    if location:
        query = query.filter(Listing.location.contains(location))
    if state:
        query = query.filter(Listing.state.contains(state))
    if amenities:
        for amenity in amenities:
            query = query.filter(Listing.amenities.contains(amenity.strip()))
    if form.check_in.data and form.check_out.data:
        query = query.outerjoin(Booking).group_by(Listing.id).having(
            db.func.count(db.case([(db.and_(Booking.start_date > form.check_out.data, Booking.end_date < form.check_in.data), 1)], else_=0)) == 0
        )

    listings = query.all()
    return render_template('search_results.html', listings=listings, search_term=search_term, form=form)


@app.route("/user/<string:username>")
def user_listings(username):
    user = User.query.filter_by(username=username).first_or_404()
    listings = Listing.query.filter_by(owner=user).all()
    bookings = Booking.query.filter_by(user=user).all()
    return render_template('user_listings.html', listings=listings, bookings=bookings, user=user)


@socketio.on('message')
def handle_message(data):
    print('Received message:', data)

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


@app.route('/reply_message', methods=['POST'])
def reply_message():
    user = current_user
    recipient_username = request.form.get('recipient')
    message_body = request.form.get('message', '')
    recipient = User.query.filter_by(username=recipient_username).first()
    file = request.files.get('file')

    if recipient:
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            message = Message(body=message_body, sender=current_user, recipient=recipient, file_path=file_path)
        else:
            message = Message(body=message_body, sender=current_user, recipient=recipient)
            
        db.session.add(message)
        db.session.commit()
        flash('Your reply has been sent!', 'success')
        return render_template('chat.html', user=user, recipient=recipient)
    else:
        flash('Recipient not found!', 'danger')
    return redirect(url_for('inbox'))


@app.route("/inbox", methods=['GET'])
@login_required
def inbox():
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
    return render_template('inbox.html', title='Inbox', messages=messages)


@app.route('/inbox/<username>', methods=['GET', 'POST'])
@login_required
def chat(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(body=form.body.data, sender=current_user, recipient=user)
        db.session.add(message)
        db.session.commit()
        flash('Your reply has been sent!', 'success')
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) & (Message.recipient_id == user.id) |
        (Message.sender_id == user.id) & (Message.recipient_id == current_user.id)
    ).order_by(Message.timestamp.asc()).all()
    return render_template('chat.html', user=user, form=form, messages=messages)


@app.route("/review/<int:listing_id>", methods=['GET', 'POST'])
@login_required
def add_review(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(rating=form.rating.data, comment=form.comment.data, reviewer=current_user, listing=listing)
        db.session.add(review)
        db.session.commit()
        flash('Your review has been added!', 'success')
        return redirect(url_for('home'))
    return render_template('review.html', title='Add Review', form=form, listing=listing)


@app.route("/profile/<username>", methods=['GET', 'POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = UpdateUserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    return render_template('profile.html', title=f'{user.username}\'s Profile', user=user, form=form)

@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        current_user.country_code = form.country_code.data
        current_user.phone_number = form.phone_number.data

        if form.image.data:
            picture_file = save_picture(form.image.data)
            current_user.image_file = picture_file
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
        #form.image_file.data = current_user.image_file
    image_url = url_for('static', filename='images/' + current_user.image_file)
    return render_template('edit_profile.html', title='Edit Profile', form=form, image_url=image_url)


@app.route('/list-your-property')
def list_property():
    listings = Listing.query.all()

    # Ensure listings is a list of objects, not strings
    if listings and isinstance(listings[0], str):
        listings = json.loads(listings)

    return render_template('list_property.html', listings=listings)


@app.route("/listing/new", methods=['GET', 'POST'])
@login_required
def new_listing():
    form = ListingForm()
    # Populate state choices
    form.state_id.choices = [(state.id, state.name) for state in State.query.order_by(State.name).all()]
    # Populate amenity choices
    form.amenities.choices = [(amenity.id, amenity.name) for amenity in Amenity.query.order_by(Amenity.name).all()]
    if form.validate_on_submit():
        listing = Listing(
            title=form.title.data,
            description=form.description.data,
            owner=current_user,
            currency=form.currency.data,
            price=form.price.data,
            country=form.country.data,
            city=form.city.data,
            state_id=form.state_id.data,
            address=form.address.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data
        )

        # Add selected amenities to the listing
        selected_amenities = Amenity.query.filter(Amenity.id.in_(form.amenities.data)).all()
        for amenity in selected_amenities:
            listing.amenities.append(ListingAmenity(amenity=amenity))

        db.session.add(listing)
        
        # Save images after creating the listing
        if form.image.data:
            for image_file in form.image.data:
                image_filename = save_picture(image_file)
                new_image = Image(file_name=image_filename, listing_id=listing.id)
                db.session.add(new_image)
        else:
            default_image = Image(file_name='default.jpg', listing_id=listing.id)
            db.session.add(default_image)

        db.session.commit()
        flash('Your listing has been created!', 'success')
        return redirect(url_for('listings'))
    return render_template('listing.html', title='New Listing', form=form)


@app.route("/listings", methods=['GET', 'POST'])
def listings():
    page = request.args.get('page', 1, type=int)
    listings = Listing.query.paginate(page=page, per_page=10, error_out=False)
    user_currency = current_user.preferred_currency if current_user.is_authenticated else 'USD'
    
    for listing in listings.items:
        if listing.currency != user_currency:
            converted_price, currency = convert_currency(float(listing.price), listing.currency, user_currency)
            currency_symbol = get_currency_symbol(user_currency)
            price_with_currency = f"{currency_symbol}{converted_price:,.2f}"
        else:
            currency_symbol = get_currency_symbol(listing.currency)
            converted_price, currency = listing.price, listing.currency
            price_with_currency = f"{currency_symbol} {listing.price:,.2f}"

    return render_template('listings.html', listings=listings, price=converted_price, currency=user_currency, price_with_currency=price_with_currency)


def convert_currency(amount, from_currency, to_currency):
    api_key = '3b1249bc5574e03487c01d2c'
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        data = response.json()
        
        if 'conversion_rates' not in data:
            logging.error("Conversion rates not found in API response.")
            raise ValueError("Invalid response from currency conversion API.")
        
        if to_currency not in data['conversion_rates']:
            logging.error(f"Currency '{to_currency}' not found in conversion rates.")
            raise KeyError(f"Currency '{to_currency}' not found.")
        
        rate = data['conversion_rates'][to_currency]
        converted_amount = float(amount) * rate
        return round(converted_amount, 2), to_currency
    
    except (requests.exceptions.RequestException, ValueError) as e:
        logging.error(f"Request to currency conversion API failed: {e}")
        return amount, from_currency


@app.route("/listing/<int:listing_id>", methods=['GET', 'POST'])
def listing(listing_id):
    user = current_user
    listing = Listing.query.get_or_404(listing_id)
    user_currency = current_user.preferred_currency if current_user.is_authenticated else 'USD'
    
    if listing.currency != user_currency:
        converted_price, currency = convert_currency(float(listing.price), listing.currency, user_currency)
        currency_symbol = get_currency_symbol(user_currency)
        price_with_currency = f"{currency_symbol}{converted_price:,.2f}"
    else:
        currency_symbol = get_currency_symbol(listing.currency)
        converted_price, currency = listing.price, listing.currency
        price_with_currency = f"{currency_symbol} {listing.price:,.2f}"

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
    return render_template('listing.html', title=listing.title, listing=listing, form=form, reviews=reviews, user=user, price=converted_price, currency=user_currency, price_with_currency=price_with_currency)


def convert_currency(amount, from_currency, to_currency):
    api_key = '3b1249bc5574e03487c01d2c'
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        data = response.json()
        
        if 'conversion_rates' not in data:
            logging.error("Conversion rates not found in API response.")
            raise ValueError("Invalid response from currency conversion API.")
        
        if to_currency not in data['conversion_rates']:
            logging.error(f"Currency '{to_currency}' not found in conversion rates.")
            raise KeyError(f"Currency '{to_currency}' not found.")
        
        rate = data['conversion_rates'][to_currency]
        converted_amount = float(amount) * rate
        return round(converted_amount, 2), to_currency
    
    except (requests.exceptions.RequestException, ValueError) as e:
        logging.error(f"Request to currency conversion API failed: {e}")
        return amount, from_currency


@app.route("/listing/<int:listing_id>/book", methods=['GET', 'POST'])
@login_required
def book_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    form = BookingForm()
    if form.validate_on_submit():
        if listing.is_available(form.start_date.data, form.end_date.data):
            booking = Booking(
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                user=current_user,
                listing=listing
            )
            db.session.add(booking)
            db.session.commit()
            flash('Booking confirmed!', 'success')
            return redirect(url_for('listings'))
        else:
            flash('Listing is not available for the selected dates.', 'danger')
    return render_template('book_listing.html', title='Book Listing', form=form, listing=listing)


@app.route('/bookings')
@login_required
def bookings():
    bookings = Booking.query.filter_by(user=current_user).all()
    return render_template('bookings.html', title='Bookings', bookings=bookings)


@app.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user != current_user:
        abort(403)
    db.session.delete(booking)
    db.session.commit()
    flash('Booking cancelled.', 'success')
    return redirect(url_for('bookings'))


@app.route('/set_currency', methods=['GET', 'POST'])
def set_currency():
    form = PreferredCurrencyForm()
    if form.validate_on_submit():
        current_user.preferred_currency = form.currency.data
        db.session.commit()
        flash('Preferred currency updated!', 'success')
        return redirect(url_for('home')) 
    return render_template('set_currency.html', form=form)


@app.route("/delete_listing/<int:listing_id>", methods=['GET', 'POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.owner != current_user:
        abort(403)
    db.session.delete(listing)
    db.session.commit()
    flash('Your listing has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/save_location', methods=['POST'])
@login_required
def save_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # save the location data to the user profile or database as needed
    current_user.latitude = latitude
    current_user.longitude = longitude
    db.session.commit()

    return jsonify({'status': 'success'}), 200


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


@app.route('/update_listing/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def update_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    
    # Ensuring that only the listing owner can update the listing
    if listing.owner != current_user:
        flash('You do not have permission to update this listing.', 'danger')
        return redirect(url_for('listing', listing_id=listing.id))
    
    form = ListingForm()
    # Populate state choices
    form.state_id.choices = [(state.id, state.name) for state in State.query.order_by(State.name).all()]
    # Populate amenity choices
    form.amenities.choices = [(amenity.id, amenity.name) for amenity in Amenity.query.order_by(Amenity.name).all()]

    # Populate form with the existing data on GET request
    if request.method == 'GET':
        form.title.data = listing.title
        form.description.data = listing.description
        form.currency.data = listing.currency
        form.price.data = listing.price
        form.state_id.data = listing.state_id
        form.city.data = listing.city
        form.address.data = listing.address
        form.latitude.data = listing.latitude
        form.longitude.data = listing.longitude
        form.amenities.data = [amenity.id for amenity in listing.amenities]

    if form.validate_on_submit():
        listing.title = form.title.data
        listing.description = form.description.data
        listing.currency = form.currency.data
        listing.price = form.price.data
        listing.state_id = form.state_id.data
        listing.city = form.city.data
        listing.address = form.address.data
        listing.latitude = form.latitude.data
        listing.longitude = form.longitude.data

        # Update the listing's amenities
        selected_amenity_ids = form.amenities.data
        
        if not selected_amenity_ids:
            flash('Please select at least one amenity.', 'warning')
            return render_template('update_listing.html', title='Update Listing', form=form, listing=listing)
        
        selected_amenities = Amenity.query.filter(Amenity.id.in_(selected_amenity_ids)).all()
        
        # Clear existing amenities
        db.session.query(ListingAmenity).filter_by(listing_id=listing.id).delete()
        
        # Add new amenities
        for amenity in selected_amenities:
            listing_amenity = ListingAmenity(listing_id=listing.id, amenity_id=amenity.id)
            db.session.add(listing_amenity) 
            
        
        try:
            # Handle image updates if a new image is uploaded
            if form.image.data:
                image_filenames = save_picture(form.image.data)

                # Check if image_filenames is a list
                if isinstance(image_filenames, list):
                    # Add multiple images
                    for filename in image_filenames:
                        new_image = Image(file_name=filename, listing=listing)
                        db.session.add(new_image)
                else:
                    # Add single image
                    new_image = Image(file_name=image_filenames, listing=listing)
                    db.session.add(new_image)
        except ValueError as e:
            flash(str(e), 'danger')

        try:
            db.session.commit()
            flash('Your listing has been updated!', 'success')
            return redirect(url_for('listing', listing_id=listing.id))
        except IntegrityError as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'danger')

    return render_template('update_listing.html', title='Update Listing', form=form, listing=listing)


@app.route('/filter_listings', methods=['POSt'])
def filter_listings():
    """Filter listings based on user input."""
    # Get query parameters
    price_filter = request.json.get('price_filter')
    rating_filter = request.json.get('rating_filter')
    amenities_filter = request.json.get('amenities_filter')

    # Apply filters to listings query
    query = Listing.query

    if price_filter:
        # Assuming price_filter is a dictionary with min and max values
        query = query.filter(Listing.price.between(price_filter['min'], price_filter['max']))

    if rating_filter:
        # Assuming rating_filter is a minimum rating value
        query = query.filter(Listing.rating >= rating_filter)
    
    if amenities_filter:
        # Assuming amenities_filter is a list of required amenities
        query = query.filter(Listing.amenities.contains(amenities_filter))

    # Execute the query and get the results
    filtered_listings = query.all()

    # Convert listings to JSON
    result = []
    for listing in filtered_listings:
        result.append({
            'id': listing.id,
            'title': listing.title,
            'price': listing.price,
            'rating': listing.rating,
            'amenities': listing.amenities,
            # Add other relevant fields here
        })

    return jsonify(result)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to login', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


#@app.before_request
@login_required
def check_preferred_currency():
    if current_user.is_authenticated and not current_user.preferred_currency:
        if request.endpoint != 'set_currency':
            return redirect(url_for('set_currency'))


@app.route('/get_states', methods=['GET'])
def get_states():
    country_code = request.args.get('country_code')
    if not country_code:
        return jsonify({'error': 'Country code is required'}), 400
    
    response = requests.get(f'https://restcountries.com/v3.1/alpha/{country_code}')
    if response.status_code == 200:
        country_data = response.json()
        states = country_data.get('subregions', [])
        return render_template('states.html', states=states)
    else:
        return "Error retrieving data", response.status_code


@app.route('/status')
@login_required
def status():
    user = User.query.get(current_user.id)
    user.last_seen = datetime.utcnow()
    db.session.commit()
    return jsonify({'status': 'online'})

@socketio.on('connect')
def handle_connect():
    emit('status_update', {'user_id': current_user.id, 'status': 'online'}, broadcast=True)
    # Check and update statuses of all users
    status_updates = check_status().json
    for update in status_updates:
        emit('status_update', update, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    emit('status_update', {'user_id': current_user.id, 'status': 'offline'}, broadcast=True)


@app.route('/check_status')
def check_status():
    users = User.query.all()
    status_updates = []

    for user in users:
        if user.last_seen:
            delta = datetime.utcnow() - user.last_seen
            if delta.total_seconds() > 300:
                status = 'offline'
            else:
                status = 'online'
        else:
            status = 'offline'

        status_updates.append({'user_id': user.id, 'status': status})

    return jsonify(status_updates)


def update_listing_amenity(amenity_id, listing_id):
    try:
        # Ensure both IDs are not None
        if listing_id is None or amenity_id is None:
            raise ValueError("Both listing_id and amenity_id must be provided")

        # Verify the listing exists
        listing = Listing.query.get(listing_id)
        if listing is None:
            raise ValueError(f"Listing with ID {listing_id} does not exist")

        # Verify the amenity exists
        amenity = Amenity.query.get(amenity_id)
        if amenity is None:
            raise ValueError(f"Amenity with ID {amenity_id} does not exist")

        # Create or update the association
        existing_association = ListingAmenity.query.filter_by(listing_id=listing_id, amenity_id=amenity_id).first()
        
        if existing_association:
            # Update existing association (if needed)
            pass  # No update needed since we're just confirming the association exists
        else:
            # Create new association
            new_association = ListingAmenity(listing_id=listing_id, amenity_id=amenity_id)
            db.session.add(new_association)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error updating listing amenity: {str(e)}")
        return False


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
