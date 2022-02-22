import os
from flask_admin import Admin
from models import db, User, Message, Network, Tag, College, Faculty, Class, File, Coll, Comment, LikedFiles, LikedColls
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    
    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Message, db.session))
    admin.add_view(ModelView(Network, db.session))
    admin.add_view(ModelView(Tag, db.session))
    admin.add_view(ModelView(College, db.session))
    admin.add_view(ModelView(Faculty, db.session))
    admin.add_view(ModelView(Class, db.session))
    admin.add_view(ModelView(File, db.session))
    admin.add_view(ModelView(Coll, db.session))
    admin.add_view(ModelView(Comment, db.session))
    admin.add_view(ModelView(LikedFiles, db.session))
    admin.add_view(ModelView(LikedColls, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))