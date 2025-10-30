import pytest
from flask import Flask
from flask_login import LoginManager

from services.user.app.extensions import db as _db
from services.user.app.routes.auth_router import auth_bp
from services.user.app.routes.oauth_router import oauth_bp
from services.user.app.routes.profile_router import profile_bp
from services.user.app.models.user_model import User


class TestingConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test_secret'

@pytest.fixture(scope='session')
def app():
    app = Flask(__name__)
    app.config.from_object(TestingConfig)
    _db.init_app(app)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(oauth_bp, url_prefix='/api/oauth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    import services.user.app.controllers.auth_controller as auth_controller
    auth_controller.limiter = type('DummyLimiter', (), {'limit': lambda *a, **k: (lambda f: f)})()

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope='function')
def db_session(app):
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        # Use the default session
        _db.session.bind = connection
        yield _db.session
        transaction.rollback()
        connection.close()
        _db.session.remove()

@pytest.fixture(scope='function')
def client(app, db_session):
    return app.test_client()
