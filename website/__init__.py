from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
DB_NAME = "database.db"



def create_app():
    from .flask_waf import Waf
    app = Flask(__name__)
    Waf(app)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin/')
    from .models import User, Urls,Admin
    
    with app.app_context():
        db.create_all()
        username = "admin"
        email = "admin@gmail.com"
        password = "admin"
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        result = Admin.query.filter_by(username=username).first() or Admin.query.filter_by(email=email).first()
        if not result:
            new_admin = Admin(username=username, email=email, password=hashed_password)
            db.session.add(new_admin)
            db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = 'views.home'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
