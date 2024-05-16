from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
import re
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    id_passport_no = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String, nullable=False)

    # Define relationship with corruption reports
    corruption_reports = db.relationship('CorruptionReport', backref='whistleblower', lazy='dynamic')
    # Define relationship with public petitions
    public_petitions = db.relationship('PublicPetition', backref='whistleblower', lazy='dynamic')

    # Define serialization rules
    serialize_rules = ('-corruption_reports.whistleblower', '-public_petitions.whistleblower')

    # Validate role
    @validates('role')
    def validate_role(self, key, role):
        if role not in ('citizen', 'admin'):
            raise ValueError("Role must be either 'citizen' or 'admin'.")
        return role

    # Validate email format
    @validates('email')
    def validate_email(self, key, email):
        assert '@' in email
        assert re.match(r"[^@]+@[^@]+\.[^@]+", email), "Invalid email format"
        return email

    # Validate password format and hash it
    @validates('password')
    def validate_password(self, key, password):
        assert len(password) > 8, "Password must be at least 8 characters long"
        assert re.search(r"[A-Z]", password), "Password should contain at least one uppercase letter"
        assert re.search(r"[a-z]", password), "Password should contain at least one lowercase letter"
        assert re.search(r"[0-9]", password), "Password should contain at least one digit"
        return generate_password_hash(password)

    # Verify password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    # Check if user is admin
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f"<User {self.fullname}, {self.email}, {self.role}>"



class CorruptionReport(db.Model):
    __tablename__ = 'corruption_reports'

    id = db.Column(db.Integer, primary_key=True)
    govt_agency = db.Column(db.String(200), nullable=False)
    county = db.Column(db.String(200), nullable=False)    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(600), nullable=False)
    media = db.Column(db.String)
    status = db.Column(db.String, default='Pending')
    location_url = db.Column(db.String, nullable=True)
    longitude = db.Column(db.Float, default=0.0)
    latitude = db.Column(db.Float, default=0.0)
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # relationships
    corruption_resolution = db.relationship('CorruptionResolution', backref='related_report')


class CorruptionResolution(db.Model):
    __tablename__ = 'corruption_resolutions'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, nullable=False)
    justification = db.Column(db.String, nullable=False)
    additional_comments = db.Column(db.String(600), nullable=True)
    # foreign keys
    record_id = db.Column(db.Integer, db.ForeignKey('corruption_reports.id'))



class PublicPetition(db.Model):
    __tablename__ = 'public_petitions'

    id = db.Column(db.Integer, primary_key=True)
    govt_agency = db.Column(db.String(200), nullable=False)
    county = db.Column(db.String(200), nullable=False)
    location_url =db.Column(db.String, nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(600), nullable=False)
    media = db.Column(db.String)
    status = db.Column(db.String, default='Pending')
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # relationships
    petition_resolution = db.relationship('PetitionResolution', backref='related_petition')



class PetitionResolution(db.Model):
    __tablename__ = 'petition_resolutions'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, nullable=False)
    justification = db.Column(db.String, nullable=False)
    additional_comments = db.Column(db.String(600), nullable=True)
    # foreign keys
    record_id = db.Column(db.Integer, db.ForeignKey('public_petitions.id'))

