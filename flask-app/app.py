from flask import Flask, jsonify, request
from flask_migrate import Migrate
from datetime import datetime, timedelta
from models import User
from models import PasswordResetToken
from models import db
from werkzeug.security import generate_password_hash, check_password_hash
from flasgger import Swagger
import random
import string
import cloudinary
import cloudinary.uploader
import jwt
import os 
import base64


# Set the working directory to the directory where your Flask app resides
app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)

# Initialize Flask app
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Auth and Cloudinary API docs',
    'uiversion': 3
}
swagger = Swagger(app)

# Configure Cloudinary
from utils import cloudconfig
cloudconfig

# Generating JWT secret key
secret_key = base64.b64encode(os.urandom(24)).decode('utf-8')

# Configure database path
db_path = os.path.join(app_dir, "app.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

# Bind the SQLAlchemy instance to the Flask app
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Routes
@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    ---
    tags:
      - Authentication
    parameters:
      - name: fullname
        in: body
        type: string
        required: true
        description: User's full name
      - name: email
        in: body
        type: string
        required: true
        description: User's email address
      - name: password
        in: body
        type: string
        required: true
        description: User's password
      - name: id_passport_no
        in: body
        type: string
        required: true
        description: User's ID or passport number
      - name: role
        in: body
        type: string
        required: true
        description: User's role
      - name: profile_picture
        in: body
        type: string
        required: false
        description: URL to user's profile picture
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
              description: Registration success message
      400:
        description: Bad request, invalid input data
    """
    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')
    password = data.get('password')
    id_passport_no = data.get('id_passport_no')
    role = data.get('role')
    profile_picture = data.get('profile_picture')

    # Check if all required fields are provided
    if not (fullname and email and password and id_passport_no and role):
        return jsonify({'message': 'All required fields must be provided'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(fullname=fullname, email=email, password=hashed_password, id_passport_no=id_passport_no, role=role, profile_picture=profile_picture)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    fullname = data.get('fullname')
    password = data.get('password')

    user = User.query.filter_by(fullname=fullname).first()

    if user and check_password_hash(user.password, password):
        # Generate token with an expiration time
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode({'user_id': user.id, 'exp': expiration_time}, secret_key, algorithm='HS256')
        return jsonify({'message': 'Login successful', 'token': token})
    else:
        return jsonify({'message': 'Invalid fullname or password'}), 401

# Helper function to decode the token
def decode_token(token):
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token has expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'



if __name__ == '__main__':
    app.run(debug=True)
