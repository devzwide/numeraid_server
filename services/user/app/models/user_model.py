import datetime

from flask_login import UserMixin
from sqlalchemy import CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=True, index=True)

    password_hash = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)

    social_provider_id = db.Column(db.String(255), unique=True, index=True, nullable=True)
    social_provider = db.Column(db.String(50), nullable=True)

    profile_picture_url = db.Column(db.Text, nullable=True)

    role = db.Column(
        db.String(20),
        nullable=False,
        index=True
    )

    __table_args__ = (
        CheckConstraint(
            role.in_(['student', 'staff', 'admin']),
        ),
    )

    is_active = db.Column(db.Boolean, default=True)
    consent_given = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    staff = db.relationship('Staff', backref='user', uselist=False, cascade="all, delete-orphan")
    student = db.relationship('Student', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes the given password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Validates a password against the stored hash."""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(username={self.username or self.email}, role={self.role})>"

    def get_id(self):
        """Required by Flask-Login."""
        return str(self.user_id)


class Staff(db.Model):
    __tablename__ = 'staff'

    staff_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), primary_key=True)

    department = db.Column(db.String(100), index=True, nullable=True)
    feedback = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    def __repr__(self):
        return f"<Staff(id={self.staff_id}, department={self.department})>"


class Student(db.Model):
    __tablename__ = 'student'

    student_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), primary_key=True)

    faculty = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False, index=True)

    year_of_study = db.Column(db.Integer, nullable=True)
    medical_proof_path = db.Column(db.String(255), nullable=True)
    application_status = db.Column(db.String(50), default='Pending')
    has_completed_onboarding = db.Column(db.Boolean, default=False)
    feedback = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    def __repr__(self):
        return f"<Student(id={self.student_id}, course={self.course}, status={self.application_status})>"