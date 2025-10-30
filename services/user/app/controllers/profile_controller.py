from flask import jsonify
from flask_login import current_user

from ..extensions import db

def get_profile():
    user = current_user
    return jsonify({
        "email": user.email,
        "username": user.username,
        "name": user.name,
        "surname": user.surname,
        "role": user.role,
        "profile_picture_url": user.profile_picture_url
    }), 200

def update_profile(req):
    user = current_user
    data = req.get_json()
    user.name = data.get('name', user.name)
    user.surname = data.get('surname', user.surname)
    user.username = data.get('username', user.username)
    db.session.commit()
    return jsonify({"message": "Profile updated."}), 200