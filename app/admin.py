from flask import redirect, url_for
from flask_admin import AdminIndexView, Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app.models import User, Listing, Review, Message, Booking, Chat
from app import app, db

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# In app/__init__.py, update the admin setup:
from .admin import MyModelView, MyAdminIndexView

admin = Admin(app, name='Admin', template_mode='bootstrap5', index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Listing, db.session))
admin.add_view(MyModelView(Review, db.session))
admin.add_view(MyModelView(Message, db.session))
admin.add_view(MyModelView(Booking, db.session))
