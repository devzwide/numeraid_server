from flask import Blueprint

from ..controllers.oauth_controller import google_auth, google_callback

oauth_bp = Blueprint('oauth', __name__)

@oauth_bp.route('/google/auth')
def google_auth_route():
    return google_auth()

@oauth_bp.route('/google/callback')
def google_callback_route():
    return google_callback()
