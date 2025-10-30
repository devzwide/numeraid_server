from flask import Blueprint

from .auth_router import auth_bp
from .oauth_router import oauth_bp
from .profile_router import profile_bp

router_bp = Blueprint('router', __name__)

router_bp.register_blueprint(auth_bp, url_prefix='/auth')
router_bp.register_blueprint(oauth_bp, url_prefix='/oauth')
router_bp.register_blueprint(profile_bp, url_prefix='/profile')