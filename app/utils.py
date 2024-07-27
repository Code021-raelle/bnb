from flask_mail import Message
from flask_mail import Mail
from flask import url_for


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


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='admin@myapp.com', 
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this mail and no changes will be made.
'''
    mail.send(msg)