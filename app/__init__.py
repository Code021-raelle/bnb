from flask import Flask, request, session
from flask_admin import Admin
from flask_socketio import SocketIO, emit
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from authlib.integrations.flask_client import OAuth
#from flask_babelex import Babel, lazy_gettext as _
import stripe
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'akinshola'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://code021:gabriel@localhost/bnb_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Maximum file size, e.g., 16MB
#stripe.api_key = app.config['']

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
#babel = Babel(app)
#babel.init_app(app)
socketio = SocketIO(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

google_bp = make_google_blueprint(client_id=os.getenv('GOOGLE_CLIENT_ID'), client_secret=os.getenv('GOOGLE_CLIENT_SECRET'), redirect_to='google_login')
facebook_bp = make_facebook_blueprint(client_id=os.getenv('FACEBOOK_CLIENT_ID'), client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'), redirect_to='facebook_login')

app.register_blueprint(google_bp, url_prefix='/login')
app.register_blueprint(facebook_bp, url_prefix='/login')

oauth = OAuth(app)
oauth.register(
    name='apple',
    client_id=os.getenv('APPLE_CLIENT_ID'),
    client_secret=os.getenv('APPLE_CLIENT_SECRET'),
    authorize_url='https://appleid.apple.com/auth/authorize',
    authorize_params=None,
    authorize_callback_url=os.getenv('APPLE_REDIRECT_URI'),
    access_token_url='https://appleid.apple.com/auth/token',
    access_token_params=None,
    client_kwargs={'scope': 'name email'}
)

#@babel.localeselector
#def get_locale():
    # Determine the locale from the user preferences stored in the session
    #override = request.args.get('lang')
    #if override:
        #session['lang'] = override
    #return session.get('lang', 'en')

# Default locale
#babel.default_locale = 'en'

# Supported languages
#babel.supported_locales = ['en', 'es', 'fr']

from app import routes, models, forms, admin
