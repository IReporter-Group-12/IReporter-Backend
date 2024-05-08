from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    _password_hash = db.Column(db.String)
    # id_password_no = db.Column(db.Integer(20), nullable=False)

    #Relationships
    redFlagRecord = db.Relationship('RedFlagRecord', backref='user')
    intervetnionRecord = db.Relationship('InterventionRecord', backref='user')


class RedFlagRecord(db.Model):
    __tablename__ = 'redFlagRecords'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(600), nullable=False)
    location =db.Column(db.String, nullable=True)
    media = db.Column(db.String)
    status = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class InterventionRecord(db.Model):
    __tablename__ = 'interventionRecords'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(600), nullable=False)
    location =db.Column(db.String, nullable=True)
    media = db.Column(db.String)
    status = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)