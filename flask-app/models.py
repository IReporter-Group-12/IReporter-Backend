from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.postgresql import ARRAY


db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    id_passport_no = db.Column(db.Integer, nullable=True)
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
    media = db.Column(ARRAY(db.String), nullable=True)    
    status = db.Column(db.String, default='Pending')
    longitude = db.Column(db.Float, default=0.0)
    latitude = db.Column(db.Float, default=0.0)
    admin_comments = db.Column(db.String, nullable=True)
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)



class PublicPetition(db.Model, SerializerMixin):
    __tablename__ = 'public_petitions'

    serialize_only = ('id', 'govt_agency', 'county', 
                      'title', 'description', 'media', 'status', 'latitude', 'longitude', 'user_id', 'admin_comments')
    serialize_rules = ()

    id = db.Column(db.Integer, primary_key=True)
    govt_agency = db.Column(db.String(200), nullable=False)
    county = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(600), nullable=False)
    media = db.Column(ARRAY(db.String), nullable=True)    
    status = db.Column(db.String, default='Pending')
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)
    admin_comments = db.Column(db.String, nullable=True)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


