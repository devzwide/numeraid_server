import jwt
import requests
import datetime

from flask_login import login_user
from sqlalchemy.exc import IntegrityError
from flask import jsonify, redirect, current_app, request

from ..extensions import db
from ..models.user_model import User

UTC = datetime.timezone.utc


def google_auth():
    client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    redirect_uri = current_app.config.get("GOOGLE_REDIRECT_URI")

    if not client_id or not redirect_uri:
        return jsonify({"error": "Google OAuth not configured"}), 500

    scope = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scope),
        'access_type': 'offline',
        'prompt': 'consent'
    }

    from requests.compat import urlencode
    return redirect(f"{auth_url}?{urlencode(params)}")


def google_callback():
    client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    client_secret = current_app.config.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = current_app.config.get("GOOGLE_REDIRECT_URI")

    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    try:
        response = requests.post(token_url, data=payload, timeout=10)
        response.raise_for_status()
        tokens = response.json()
    except Exception as e:
        return jsonify({"error": "Failed to exchange code for tokens"}), 500

    id_token = tokens.get('id_token')
    try:
        user_info = jwt.decode(id_token, options={"verify_signature": False}, algorithms=["RS256"])
    except Exception as e:
        return jsonify({"error": "Invalid token from Google"}), 500

    email = user_info.get('email')
    if not email:
        return jsonify({"error": "Google account missing email"}), 400

    google_id = user_info.get('sub')
    name = user_info.get('given_name', '')
    surname = user_info.get('family_name', '')
    picture = user_info.get('picture')

    user = User.query.filter_by(social_provider_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.social_provider_id = google_id
            user.social_provider = 'Google'
            db.session.flush()
        else:
            try:
                user = User(
                    email=email,
                    name=name,
                    surname=surname,
                    username=None,
                    role='student',
                    social_provider='Google',
                    social_provider_id=google_id,
                    profile_picture_url=picture
                )
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return jsonify({"error": "Database constraint violation"}), 500

    user.last_login = datetime.datetime.now(UTC)
    db.session.commit()
    login_user(user)

    # Redirect based on user role
    return redirect(f"http://localhost:5173/{user.role}/dashboard")