from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
import re
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    id_passport_no = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String, nullable=False)
    # relationships
    corruption_report = db.relationship('CorruptionReport', backref='whistleblower')
    public_petition = db.relationship('PublicPetition', backref='whistleblower')

    def __repr__(self) -> str:
        return f"User : {self.fullname}\nEmail : {self.email}\nIdentification No. : {self.id_passport_no}\nRole: {self.role}"

    @property
    def is_admin(self):
        if self.role == 'admin':
            return True
        else:
            return False

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



class PublicPetition(db.Model, SerializerMixin):
    __tablename__ = 'public_petitions'

    serialize_only = ('id', 'govt_agency', 'county', 'location_url', 
                      'title', 'description', 'media', 'status', 'user_id')
    serialize_rules = ()

    id = db.Column(db.Integer, primary_key=True)
    govt_agency = db.Column(db.String(200), nullable=False)
    county = db.Column(db.String(200), nullable=False)
    location_url =db.Column(db.String, nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(600), nullable=False)
    media = db.Column(db.String)
    status = db.Column(db.String, default='Pending')
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # relationships
    resolution = db.relationship('PetitionResolution', back_populates='petition')



class PetitionResolution(db.Model, SerializerMixin):
    __tablename__ = 'petition_resolutions'

    serialize_only = ('id', 'status', 'justification', 'additional_comments', 
                      'petition.id', 'petition.govt_agency', "petition.title", 'petition.description')
    serialize_rules = ()


    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, nullable=False)
    justification = db.Column(db.String, nullable=False)
    additional_comments = db.Column(db.String(600), nullable=True)
    # foreign keys
    record_id = db.Column(db.Integer, db.ForeignKey('public_petitions.id'))

    petition = db.relationship('PublicPetition', back_populates = 'resolution')

