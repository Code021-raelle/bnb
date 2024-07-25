from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields import DateField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from app.models import User

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
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png'])])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired(), Length(min=1, max=20)])
    currency = SelectField('Currency', choices=[('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('NGN', 'NGN')])
    location = TextAreaField('Address', validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired()])
    longitude = FloatField('Longitude', validators=[DataRequired()])
    submit = SubmitField('Post Listing')


class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    min_price = IntegerField('Min Price', validators=[Optional()])
    max_price = IntegerField('Max Price', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    amenities = StringField('Amenities', validators=[Optional()])
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
    about_me = TextAreaField('About me', validators=[Length(max=140)])
    submit = SubmitField('Update')


class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


class PreferredCurrencyForm(FlaskForm):
    currency = SelectField('Preferred Currency', choices=[
        ('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('NGN', 'NGN'),
        ('JPY', 'JPY'), ('AUD', 'AUD'), ('CAD', 'CAD'), ('CHF', 'CHF'),
        ('CNY', 'CNY'), ('HKD', 'HKD'), ('NZD', 'NZD'), ('SEK', 'SEK'),
        ('SGD', 'SGD'), ('ZAR', 'ZAR')
    ])
    submit = SubmitField('Save')
