from flask import Flask, request, make_response, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
import cloudinary
import cloudinary.uploader
from models import db,CorruptionReport, CorruptionResolution


app = Flask(__name__)
app.config.from_object(ApplicationConfig)
CORS(app)
db.init_app(app)
migrate= Migrate(app, db)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return '<h1>Welcome to IReporter!</h1>'

## CorruptionReports Routes
from sqlalchemy.exc import IntegrityError

@app.route('/corruption_reports', methods=['POST'])
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
        location_url=data.get('location_url'),
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
def get_all_corruption_reports():
    reports = CorruptionReport.query.all()
    return jsonify([{
        'id': report.id,
        'govt_agency': report.govt_agency,
        'county': report.county,
        'location_url': report.location_url,
        'longitude': report.longitude,
        'latitude': report.latitude,
        'title': report.title,
        'description': report.description,
        'media': report.media,
        'status': report.status,
        'user_id': report.user_id
    } for report in reports]), 200

@app.route('/corruption_reports/<int:report_id>', methods=['GET'])
def get_corruption_report(report_id):
    report = CorruptionReport.query.get(report_id)
    if report:
        return jsonify({
            'id': report.id,
            'govt_agency': report.govt_agency,
            'county': report.county,
            'location_url': report.location_url,
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
def update_corruption_report(report_id):
    report = CorruptionReport.query.get(report_id)
    if report:
        data = request.json
        report.govt_agency = data.get('govt_agency', report.govt_agency)
        report.county = data.get('county', report.county)
        report.location_url = data.get('location_url', report.location_url)
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
def delete_corruption_report(report_id):
    report = CorruptionReport.query.get(report_id)
    if report:
        db.session.delete(report)
        db.session.commit()
        return jsonify({'message': 'Corruption report deleted successfully'}), 200
    return jsonify({'error': 'Corruption report not found'}), 404


## CorruptionResolution Routes
@app.route('/corruption_resolutions', methods=['POST'])
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





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)