from flask import Flask, request, make_response, abort, jsonify
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
import cloudinary
import cloudinary.uploader
from utils import cloudinary_config
from models import db, CorruptionReport, User, PublicPetition
from functools import wraps


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

    fullname= data.get('fullName')
    email = data.get('email')
    password = data.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    role = 'user'

    # ensure email is unique
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return make_response({'error' : 'The email provided is already linked to an existing account. Please try again'}, 400)

    if fullname and email and hashed_password and role:
        new_user = User(fullname=fullname, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return make_response({'message' : 'Registration successful!',
                            'username' : new_user.fullname,
                            'user_id' : new_user.id,
                            'role' : new_user.role}, 201)
    else:
        return make_response({'error' : 'You have entered incorrect data. Please try again.'}, 400)


# admin registration route
@app.route('/admin/register', methods=['POST'])
def admin_register():
    data = request.json

    fullname= data.get('fullName')
    email = data.get('email')
    password = data.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    staff_no = data.get('staff_no')
    role = 'admin'

    # ensure email is unique
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return make_response({'error' : 'The email provided is already linked to an existing account. Please try again'}, 400)

    if fullname and email and hashed_password and staff_no and role:
        new_user = User(fullname=fullname, email=email, password=hashed_password, id_passport_no=staff_no, role=role)
        db.session.add(new_user)
        db.session.commit()

        return make_response({'message' : 'Registration successful!',
                            'username' : new_user.fullname,
                            'user_id' : new_user.id,
                            'role' : new_user.role}, 201)
    else:
        return make_response({'error' : 'You have entered incorrect data. Please try again.'}, 400)


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
            return make_response({'message' : f'Login for Admin {current_user.fullname} successful!',
                              'user_id' : current_user.id,
                              'username' : current_user.fullname,
                              'email' : current_user.email,
                              'role' : current_user.role}, 200)
        
        return make_response({'message' : f'Login for User {current_user.fullname} successful!',
                              'user_id' : current_user.id,
                              'username' : current_user.fullname,
                              'email' : current_user.email,
                              'role' : current_user.role}, 200)
    else:
        return make_response({'error' : 'Password or username incorrect. Please try again.'}, 400)

    
# logout view
@app.route('/logout', methods=['POST'])
# @login_required
def logout():
    print(current_user)
    logout_user()
    return make_response({'message' : 'User has been logged out successfully!'}, 200)
  

## CorruptionReports Routes
@app.route('/corruption_reports', methods=['GET'])
# @admin_required
# @login_required
def get_all_corruption_reports():
    reports = CorruptionReport.query.all()
    return jsonify([{
        'id': report.id,
        'govt_agency': report.govt_agency,
        'county': report.county,
        'longitude': report.longitude,
        'latitude': report.latitude,
        'title': report.title,
        'description': report.description,
        'media': report.media,
        'status': report.status,
        'user_id': report.user_id,
        'admin_comments' : report.admin_comments
    } for report in reports]), 200

@app.route('/corruption_reports', methods=['POST'])
# @login_required
def create_corruption_report():
    data = request.json
    # Check if a similar report already exists
    existing_report = CorruptionReport.query.filter_by(
        user_id=data.get("user_id"),
        govt_agency=data.get("govt_agency"),
        county=data.get("county"),
        title=data.get("title"),
        description=data.get("description"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
    ).first()

    if existing_report:
        return jsonify({'error': 'Corruption report already exists'}), 409

    # Create a new report
    new_report = CorruptionReport(
        user_id=data.get("user_id"),
        govt_agency=data.get("govt_agency"),
        county=data.get("county"),
        title=data.get("title"),
        description=data.get("description"),
        status='Pending',
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        media = data.get('media', [None])
    )

    db.session.add(new_report)
    try:
        db.session.commit()
        return jsonify({'message': 'Corruption report created successfully', 'report_id': new_report.id}), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Failed to create corruption report due to database integrity error'}), 500


# this route returns all reports connected to a user
@app.route('/corruption_reports/<int:user_id>/', methods=['GET'])
# @admin_required
# @login_required
def get_corruption_report_by_user(user_id):
    reports = CorruptionReport.query.filter_by(user_id=user_id).all()
    if reports == None:
        return jsonify({'error': 'Corruption reports not found'}), 404
    else:
        return jsonify([{
            'id': report.id,
            'govt_agency': report.govt_agency,
            'county': report.county,
            'longitude': report.longitude,
            'latitude': report.latitude,
            'title': report.title,
            'description': report.description,
            'media': report.media,
            'status': report.status,
            'admin_comments' : report.admin_comments,
            'user_id': report.user_id
    } for report in reports]), 200


@app.route('/corruption_reports/<int:report_id>', methods=['PUT', 'PATCH'])
# @login_required
def user_update_corruption_report(report_id):

    report = CorruptionReport.query.get(report_id)

    if report:
        data = request.json
        if 'govt_agency' in data and data['govt_agency'] is not None:
            report.govt_agency = data['govt_agency']
        if 'county' in data and data['county'] is not None:
            report.county = data['county']
        if 'longitude' in data and data['longitude'] is not None:
            report.longitude = data['longitude']
        if 'latitude' in data and data['latitude'] is not None:
            report.latitude = data['latitude']
        if 'description' in data and data['description'] is not None:
            report.description = data['description']
        if 'media' in data and data['media'] is not None:
            report.media = data['media']

        try:
            db.session.commit()
            return make_response(
                {"message": 'Corruption report updated successfully'}, 200
            )
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "This error occurred due to database integrity issues"}), 500
        
    return jsonify({'error': 'Corruption report not found'}), 404


@app.route('/admin_corruption_reports/<int:report_id>', methods=['PATCH'])
# @admin_required
# @login_required
def admin_update_corruption_report(report_id):

    report = CorruptionReport.query.get(report_id)

    if report:
        data = request.json
        if 'status' in data and data['status'] is not None:
            report.status = data['status']
        if 'admin_comments' in data and data['admin_comments'] is not None:
            report.admin_comments = data['admin_comments']

        db.session.commit()
        return jsonify({'message': 'Corruption report updated successfully'}), 200
    
    return jsonify({'error': 'Corruption report not found'}), 404


@app.route('/corruption_reports/<int:report_id>', methods=['DELETE'])
# @login_required
def user_delete_corruption_report(report_id):

    report = CorruptionReport.query.get(report_id)

    if report:
        db.session.delete(report)
        db.session.commit()
        return jsonify({'message': 'Corruption report deleted successfully'}), 200
    
    return jsonify({'error': 'Corruption report not found'}), 404


cloudinary_config
@app.route('/upload_report', methods=['POST'])
# @login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify ({'error': 'No file part'}), 400
    
    file= request.files['file']
    if file.filename=='':
        return jsonify ({'error': 'No selected file'}), 400
    
    try:
        #upload the file to cloudinary
        result= cloudinary.uploader.upload(file)        
        return jsonify ({'url': result['secure_url']})
    except Exception as e:
        return jsonify ({'error': str(e)})



## Public Petitions
@app.route('/public_petitions', methods=['GET', 'POST'])
# @login_required
def user_get_post_public_petitions():
    
    if request.method == 'GET':
        public_petitions = []
        for public_petition in PublicPetition.query.all():
            public_petitions.append(public_petition.to_dict())
        return jsonify(public_petitions), 200
    
    elif request.method == 'POST':
        print(request.json.get("media"))

        existing_petition = PublicPetition.query.filter_by(
            user_id=request.json.get("user_id"),
            govt_agency=request.json.get("govt_agency"),
            county=request.json.get("county"),
            title=request.json.get("title"),
            description=request.json.get("description"),
            latitude=request.json.get("latitude"),
            longitude=request.json.get("longitude"),
        ).first()

        if existing_petition:
            return make_response(
                {"error": "This Intervention Record already exists."}, 409
            )
        new_public_petition = PublicPetition(
            
            user_id=request.json.get("user_id"),
            govt_agency=request.json.get("govt_agency"),
            county=request.json.get("county"),
            title=request.json.get("title"),
            description=request.json.get("description"),
            status='Pending',
            latitude=request.json.get("latitude"),
            longitude=request.json.get("longitude"),
            media = request.json.get('media', [None])
        )
        db.session.add(new_public_petition) 

        try:
            db.session.commit()
            response = {"message": "Successfully created"}
            return make_response(response, 201)
        except IntegrityError:
            return {"error": "This error occured due to database integrity issues."}, 500
    
    
# this route gets all the reports published by a user
@app.route('/public_petitions/<int:user_id>/', methods=['GET'])
# @login_required
def get_public_petitions_by_user_id(user_id):

    public_petitions = PublicPetition.query.filter_by(user_id=user_id).all()

    if public_petitions == None:
        return {"error": "Public Petitions report not found"}, 404
    else:
        response = jsonify([petition.to_dict() for petition in public_petitions]), 200
        return response
        


@app.route('/public_petitions/<int:id>', methods=['PATCH', 'DELETE'])
# @login_required
def user_patch_delete_public_petition(id):

    public_petition = PublicPetition.query.filter(PublicPetition.id==id).first()

    if public_petition == None:
        return {"error": "Intervention report not found"}, 404
    
    else:
        
        if request.method == 'PATCH':
            data = request.json
            if 'govt_agency' in data and data['govt_agency'] is not None:
                public_petition.govt_agency = data['govt_agency']
            if 'county' in data and data['county'] is not None:
                public_petition.county = data['county']
            if 'longitude' in data and data['longitude'] is not None:
                public_petition.longitude = data['longitude']
            if 'latitude' in data and data['latitude'] is not None:
                public_petition.latitude = data['latitude']
            if 'description' in data and data['description'] is not None:
                public_petition.description = data['description']
            if 'media' in data and data['media'] is not None:
                public_petition.media = data['media']

            try:
                db.session.commit()
                return jsonify({"message": "Intervention successfully updated"}), 200
            
            except IntegrityError:
                db.session.rollback()
                return {"error": "This error occurred due to database integrity issues"}, 500
                    
        elif request.method == "DELETE":
            db.session.delete(public_petition)
            db.session.commit()

            return make_response({"message": "Intervention successfully deleted"}, 200)
    

@app.route('/admin_public_petitions/<int:id>', methods=['PATCH'])
# @admin_required
# @login_required
def admin_patch_delete_public_petition(id):

    public_petition = PublicPetition.query.filter(PublicPetition.id==id).first()

    if public_petition is None:
        return {"error": "Intervention report not found"}, 404
    
    if request.method == 'PATCH':
        data = request.json
        if 'status' in data and data['status'] is not None:
            public_petition.status = data['status']
        if 'admin_comments' in data and data['admin_comments'] is not None:
            public_petition.admin_comments = data['admin_comments']
        
        try:
            db.session.commit()
            return jsonify({"message": "Intervention successfully updated"}), 200
        
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "This error occurred due to database integrity issues"}), 500        

cloudinary_config       
@app.route('/upload_petition', methods=['POST'])
def upload_resolution_file():    
    if 'file' not in request.files:
        return jsonify({"error": "Oops!! There is no file."}), 400
    

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        #Upload file to cloudinary
        result = cloudinary.uploader.upload(file)
        return jsonify({'url': result['secure_url']})
    except Exception as e:
        return jsonify({'error':str(e)})

        


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)