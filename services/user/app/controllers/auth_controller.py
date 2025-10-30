import re
import datetime

from flask import request
from flask_login import login_user, logout_user, login_required

from ..models.user_model import User
from ..extensions import db, limiter
from ..forms import RegisterForm, LoginForm, sanitize_input


def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@limiter.limit("10 per minute")
def register():
    form = RegisterForm()

    if request.method != 'POST':
        return {"message": "Method not allowed"}, 405

    try:
        if form.validate_on_submit():
            # Sanitize and normalize inputs
            email = sanitize_input(form.email.data).lower()
            username = sanitize_input(form.username.data)
            name = sanitize_input(form.name.data)
            surname = sanitize_input(form.surname.data)

            # Validate email format
            if not is_valid_email(email):
                return {"message": "Invalid email format."}, 400

            # Check for existing user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return {"message": "Email already registered."}, 400

            # Check username uniqueness
            if username:
                existing_username = User.query.filter_by(username=username).first()
                if existing_username:
                    return {"message": "Username already taken."}, 400

            # Create new user within transaction
            with db.session.begin_nested():
                new_user = User(
                    email=email,
                    username=username,
                    name=name,
                    surname=surname,
                    role='student',
                    consent_given=form.consent.data
                )
                new_user.set_password(form.password.data)
                db.session.add(new_user)

            # Commit the transaction
            db.session.commit()

            return {"message": "User registered successfully."}, 201

        else:
            return {"message": "Form validation failed.", "errors": form.errors}, 400

    except Exception as e:
        db.session.rollback()
        return {"message": "Registration failed. Please try again."}, 500


@limiter.limit("5 per minute")
def login():
    form = LoginForm()

    if request.method != 'POST':
        return {"message": "Method not allowed"}, 405

    try:
        if form.validate_on_submit():
            # Sanitize and normalize email
            email = sanitize_input(form.email.data).lower()

            user = User.query.filter_by(email=email).first()

            # Use constant-time comparison to prevent timing attacks
            if user and user.check_password(form.password.data):
                if user.is_active:
                    login_user(user, remember=form.remember.data)
                    user.last_login = datetime.datetime.now(datetime.timezone.utc)
                    db.session.commit()
                    return {"message": "Login successful."}, 200
                else:
                    return {"message": "Account is deactivated."}, 403
            else:
                return {"message": "Invalid email or password."}, 401
        else:
            return {"message": "Form validation failed.", "errors": form.errors}, 400

    except Exception as e:
        db.session.rollback()
        return {"message": "Login failed. Please try again."}, 500


@login_required
def logout():
    try:
        logout_user()
        return {"message": "Logout successful."}, 200
    except Exception as e:
        return {"message": "Logout failed.", "error": str(e)}, 500