from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from .extensions import db, login_manager, csrf
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .models.user_model import User
    @login_manager.user_loader
    def load_user(user_id):
        if user_id is not None:
            try:
                return User.query.get(int(user_id))
            except ValueError:
                return None
        return None

    from .routes import router_bp
    app.register_blueprint(router_bp, url_prefix='/api')

    return app