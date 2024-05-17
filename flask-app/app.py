from flask import Flask, request, make_response, redirect, url_for, abort, jsonify
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
import cloudinary
import cloudinary.uploader
from models import db, CorruptionReport, CorruptionResolution, User, PublicPetition, PetitionResolution
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

  


## CorruptionReports Routes
@app.route('/corruption_reports', methods=['POST'])
@login_required
def create_corruption_report():
    data = request.json
    # Check if a similar report already exists
    existing_report = CorruptionReport.query.filter_by(
        govt_agency=data['govt_agency'],
        county=data['county'],
        title=data['title'],
        description=data['description'],
        user_id=data['user_id']
    ).first()

    if existing_report:
        return jsonify({'error': 'Corruption report already exists'}), 409

    # Create a new report
    new_report = CorruptionReport(
        govt_agency=data['govt_agency'],
        county=data['county'],
        longitude=data.get('longitude'),
        latitude=data.get('latitude'),
        title=data['title'],
        description=data['description'],
        media=data.get('media'),
        status=data.get('status', 'Pending'),
        user_id=data['user_id']
    )

    db.session.add(new_report)
    try:
        db.session.commit()
        return jsonify({'message': 'Corruption report created successfully', 'report_id': new_report.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Failed to create corruption report due to database integrity error'}), 500

@app.route('/corruption_reports', methods=['GET'])
@login_required
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
        'user_id': report.user_id
    } for report in reports]), 200

@app.route('/corruption_reports/<int:report_id>', methods=['GET'])
@login_required
def get_corruption_report(report_id):
    report = CorruptionReport.query.get(report_id)
    if report:
        return jsonify({
            'id': report.id,
            'govt_agency': report.govt_agency,
            'county': report.county,
            'longitude': report.longitude,
            'latitude': report.latitude,
            'title': report.title,
            'description': report.description,
            'media': report.media,
            'status': report.status,
            'user_id': report.user_id
        }), 200
    return jsonify({'error': 'Corruption report not found'}), 404

@app.route('/corruption_reports/<int:report_id>', methods=['PUT', 'PATCH'])
@login_required
def update_corruption_report(report_id):
    report = CorruptionReport.query.get(report_id)
    if report:
        data = request.json
        report.govt_agency = data.get('govt_agency', report.govt_agency)
        report.county = data.get('county', report.county)
        report.longitude = data.get('longitude', report.longitude)
        report.latitude = data.get('latitude', report.latitude)
        report.title = data.get('title', report.title)
        report.description = data.get('description', report.description)
        report.media = data.get('media', report.media)
        report.status = data.get('status', report.status)
        db.session.commit()
        return jsonify({'message': 'Corruption report updated successfully'}), 200
    return jsonify({'error': 'Corruption report not found'}), 404

@app.route('/corruption_reports/<int:report_id>', methods=['DELETE'])
@login_required
def delete_corruption_report(report_id):
    report = CorruptionReport.query.get(report_id)
    if report:
        db.session.delete(report)
        db.session.commit()
        return jsonify({'message': 'Corruption report deleted successfully'}), 200
    return jsonify({'error': 'Corruption report not found'}), 404



## CorruptionResolution Routes
@app.route('/corruption_resolutions', methods=['POST'])
@login_required
def create_corruption_resolution():
    data = request.json
    existing_resolution = CorruptionResolution.query.filter_by(
        status=data['status'],
        justification=data['justification'],
        additional_comments=data.get('additional_comments'),
        record_id=data['record_id']
    ).first()

    if existing_resolution:
        return jsonify({'error': 'Corruption resolution already exists'}), 409

    new_resolution = CorruptionResolution(
        status=data['status'],
        justification=data['justification'],
        additional_comments=data.get('additional_comments'),
        record_id=data['record_id']
    )

    db.session.add(new_resolution)
    try:
        db.session.commit()
        return jsonify({'message': 'Corruption resolution created successfully', 'resolution_id': new_resolution.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Failed to create corruption resolution due to database integrity error'}), 500


@app.route('/corruption_resolutions', methods=['GET'])
@login_required
def get_all_corruption_resolutions():
    resolutions = CorruptionResolution.query.all()
    return jsonify([{
        'id': resolution.id,
        'status': resolution.status,
        'justification': resolution.justification,
        'additional_comments': resolution.additional_comments,
        'record_id': resolution.record_id
    } for resolution in resolutions]), 200

@app.route('/corruption_resolutions/<int:resolution_id>', methods=['GET'])
@login_required
def get_corruption_resolution(resolution_id):
    resolution = CorruptionResolution.query.get(resolution_id)
    if resolution:
        return jsonify({
            'id': resolution.id,
            'status': resolution.status,
            'justification': resolution.justification,
            'additional_comments': resolution.additional_comments,
            'record_id': resolution.record_id
        })
    return jsonify({'error': 'Corruption resolution not found'}), 404


@app.route('/corruption_resolutions/<int:resolution_id>', methods=['PUT', 'PATCH'])
@login_required
def update_corruption_resolution(resolution_id):
    resolution = CorruptionResolution.query.get(resolution_id)
    if resolution:
        data = request.json
        resolution.status = data.get('status', resolution.status)
        resolution.justification = data.get('justification', resolution.justification)
        resolution.additional_comments = data.get('additional_comments', resolution.additional_comments)
        db.session.commit()
        return jsonify({'message': 'Corruption resolution updated successfully'})
    return jsonify({'error': 'Corruption resolution not found'}), 404

@app.route('/corruption_resolutions/<int:resolution_id>', methods=['DELETE'])
@login_required
def delete_corruption_resolution(resolution_id):
    resolution = CorruptionResolution.query.get(resolution_id)
    if resolution:
        db.session.delete(resolution)
        db.session.commit()
        return jsonify({'message': 'Corruption resolution deleted successfully'})
    return jsonify({'error': 'Corruption resolution not found'}), 404

from utils import cloudconfig
cloudconfig
@app.route('/upload_report', methods=['POST'])
@login_required
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
@login_required
def public_petitions():
    
    if request.method == 'GET':
        public_petitions = []
        for public_petition in PublicPetition.query.all():
            public_petitions.append(public_petition.to_dict())
        return make_response(public_petitions, 200)
    
    elif request.method == 'POST':
        new_public_petition = PublicPetition(
            govt_agency=request.form.get("govt_agency"),
            county=request.form.get("county"),
            title=request.form.get("title"),
            description=request.form.get("description"),
            media=request.form.get("media"),
            status=request.form.get("status"),
            latitude=request.form.get("latitude"),
            longitude=request.form.get("longitude"),
            user_id=request.form.get("user_id")
        )
        db.session.add(new_public_petition)
        db.session.commit()

        response = {"message": "Successfully created"}
        return make_response(response, 201)
    
@app.route('/petition_resolutions', methods=['GET', 'POST'])
@login_required
def petition_resolutions():
    
    if request.method == 'GET':
        petition_resolutions = []
        for petition_resolution in PetitionResolution.query.all():
            petition_resolutions.append(petition_resolution.to_dict())
        return make_response(petition_resolutions, 200)
    
    elif request.method == 'POST':
        new_pr = PetitionResolution(
            status=request.form.get("status"),
            justification=request.form.get("justification"),
            additional_comments=request.form.get("additional_comments"),
            record_id=request.form.get("record_id")
        )
        db.session.add(new_pr)
        db.session.commit()

        return make_response({
            "message": "Successfully created"
        }, 201)
    
@app.route('/public_petitions/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def public_petition(id):
    public_petition = PublicPetition.query.filter(PublicPetition.id==id).first()

    if public_petition == None:
        return {"error": "Intervention report not found"}, 404
    
    else:
        if request.method == 'GET':
            response = make_response(public_petition.to_dict(), 200)
            return response
        
        elif request.method == 'PATCH':
            for attr in request.form:
                setattr(public_petition, attr, request.form.get(attr))
            
            db.session.add(public_petition)
            db.session.commit()

            return make_response(
                {"message": "Intervention successfully updated"}, 200
            )
        
        elif request.method == "DELETE":
            db.session.delete(public_petition)
            db.session.commit()

            return make_response({"message": "Intervention successfully deleted"}, 200)
        
@app.route('/petition_resolutions/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def petition_resolution(id):
    pr = PetitionResolution.query.filter(PetitionResolution.id==id).first()
    if pr == None:
        return {"error": "Resolution record not found"}, 404
    
    else:
        if request.method == 'GET':
            response = make_response(pr.to_dict(), 200)
            return response
        
        elif request.method == 'PATCH':
            for attr in request.form:
                setattr(pr, attr, request.form.get(attr))
            
            db.session.add(pr)
            db.session.commit()

            return make_response({
                "message": "Resolution successfully updated"
            }, 200)
        
        elif request.method == 'DELETE':
            db.session.delete(pr)
            db.session.commit()

            return make_response({
                "message": "Resolution successfully deleted"
            }) 


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)