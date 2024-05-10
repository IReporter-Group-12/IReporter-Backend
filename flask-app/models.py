from datetime import datetime
from dbconfig import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(100), nullable=False)      
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    id_passport_no = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    # relationships
    corruption_report = db.relationship('CorruptionReport', backref='whistleblower')
    public_petition = db.relationship('PublicPetition', backref='whistleblower')



class PasswordResetToken(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref='reset_tokens')   

class CorruptionReport(db.Model):
    __tablename__ = 'corruption_reports'

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