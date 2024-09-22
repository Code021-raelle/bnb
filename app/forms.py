from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, MultipleFileField
from wtforms.fields import DateField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from flask_login import current_user
from app.models import User
import re

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    preferred_currency = SelectField('Preferred Currency', choices=[('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('NGN', 'NGN')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    image = MultipleFileField('Images', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired(), Length(min=1, max=20)])
    currency = SelectField('Currency', choices=[('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('NGN', 'NGN')])
    state_id = SelectField('State', coerce=int, choices=[], validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired()])
    longitude = FloatField('Longitude', validators=[DataRequired()])
    amenities = SelectMultipleField('Amenities', coerce=int, choices=[], validators=[DataRequired()])
    submit = SubmitField('Post Listing')


class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    min_price = IntegerField('Min Price', validators=[Optional()])
    max_price = IntegerField('Max Price', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    amenities = SelectMultipleField('Amenities', coerce=int)
    check_in = DateField('Check-in Date')
    check_out = DateField('Check-out Date')
    submit = SubmitField('Search')

class BookingForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Book')


class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(i, str(i)) for i in range(1, 6)], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')


class MessageForm(FlaskForm):
    recipient = StringField('Recipient', validators=[DataRequired()])
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


class EditProfileForm(FlaskForm):
    image = FileField('Profile Image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    country_code = IntegerField('Country Code', validators=[DataRequired(), NumberRange(min=0, max=9999)])
    phone_number = IntegerField('Phone Number', validators=[DataRequired(), NumberRange(min=0, max=9999999999)])
    about_me = TextAreaField('About me', validators=[Length(max=140)])
    submit = SubmitField('Update')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = kwargs.get('obj') or current_user

    def validate_phone_number(form, field):
        if field.data and not re.match(r'^\d{10}$', str(field.data)):
            raise ValidationError('Please enter a valid 10-digit phone number.')


class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    bio = TextAreaField('Bio')
    phone_number = StringField('Address')
    submit = SubmitField('Update')


class PreferredCurrencyForm(FlaskForm):
    currency = SelectField('Preferred Currency', choices=[
        ('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('NGN', 'NGN'),
        ('JPY', 'JPY'), ('AUD', 'AUD'), ('CAD', 'CAD'), ('CHF', 'CHF'),
        ('CNY', 'CNY'), ('HKD', 'HKD'), ('NZD', 'NZD'), ('SEK', 'SEK'),
        ('SGD', 'SGD'), ('ZAR', 'ZAR')
    ])
    submit = SubmitField('Save')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')
        

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
