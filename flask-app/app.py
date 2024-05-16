from flask import Flask, request, make_response, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from functools import wraps
from models import db, User


# initiate flask app
app = Flask(__name__)
app.config.from_object(ApplicationConfig)
CORS(app)

# initiate 3rd party services
db.init_app(app)
migrate= Migrate(app, db)
bcrypt = Bcrypt(app)

# initiate flask_login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# decorator to protect admin routes
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    return decorated_view

# function to load logged in user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# user registration route
@app.route('/user/register', methods=['POST'])
def user_register():
    data = request.json

    fullname= data.get('fullname')
    email = data.get('email')
    password = data.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    id_passport_no = data.get('id_passport_no')
    role = 'user'

    # ensure email is unique
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return make_response({'error' : 'The email provided is already linked to an existing account. Please try again'}, 400)

    if fullname and email and hashed_password and id_passport_no and role:
        new_user = User(fullname=fullname, email=email, password=hashed_password, id_passport_no=id_passport_no, role=role)
        db.session.add(new_user)
        db.session.commit()

        return make_response({'message' : 'Registration successful!'}, 201)

# admin registration route
@app.route('/admin/register', methods=['POST'])
def admin_register():
    data = request.json

    fullname= data.get('fullname')
    email = data.get('email')
    password = data.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    id_passport_no = data.get('id_passport_no')
    role = 'admin'

    # ensure email is unique
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return make_response({'error' : 'The email provided is already linked to an existing account. Please try again'}, 400)

    if fullname and email and hashed_password and id_passport_no and role:
        new_user = User(fullname=fullname, email=email, password=hashed_password, id_passport_no=id_passport_no, role=role)
        db.session.add(new_user)
        db.session.commit()

        return make_response({'message' : 'Registration successful!'}, 201)


# login view
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    email = data.get('email')
    password=data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        if current_user.is_admin:
            redirect(url_for('admin_dashboard'))
            return make_response({'message' : 'Admin logged in successfully!'}, 200)
        else:
            redirect(url_for('user_dashboard'))
        return make_response({'message' : 'User logged in successfully!'}, 200)
    else:
        return make_response({'error' : 'Password or username incorrect. Please try again.'}, 400)

    
# logout view
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    print(current_user)
    logout_user()
    return make_response({'message' : 'User logged out successfully!'}, 200)


# user dashboard route
@app.route('/user_dashboard', methods=['GET'])
@login_required
def user_dashboard():
    return make_response({'message' : 'This is the user dashboard'})


# admin dashboard route
@app.route('/admin_dashboard', methods=['GET'])
@admin_required
@login_required
def admin_dashboard():
    return make_response({'message' : 'This is the admin dashboard'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)