from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from models import db,CorruptionReport, CorruptionResolution


app = Flask(__name__)
app.config.from_object(ApplicationConfig)
CORS(app)
db.init_app(app)
migrate= Migrate(app, db)
bcrypt = Bcrypt(app)



@app.route('/corruption_reports', methods=['POST'])
def create_corruption_report():
    data = request.json
    new_report = CorruptionReport(
        govt_agency=data['govt_agency'],
        county=data['county'],
        location_url=data.get('location_url'),
        title=data['title'],
        description=data['description'],
        media=data.get('media'),
        status=data.get('status', 'Pending'),  
        user_id=data['user_id']  
    )
    db.session.add(new_report)
    db.session.commit()
    return jsonify({'message': 'Corruption report created successfully', 'report_id': new_report.id}), 201

@app.route('/corruption_reports/<int:report_id>', methods=['GET'])
def get_corruption_report(report_id):
    report = CorruptionReport.query.get(report_id)
    if report:
        return jsonify({
            'id': report.id,
            'govt_agency': report.govt_agency,
            'county': report.county,
            'location_url': report.location_url,
            'title': report.title,
            'description': report.description,
            'media': report.media,
            'status': report.status,
            'user_id': report.user_id
        })
    return jsonify({'error': 'Corruption report not found'}), 404

@app.route('/corruption_reports/<int:report_id>', methods=['PUT', 'PATCH'])
def update_corruption_report(report_id):
    report = CorruptionReport.query.get(report_id)
    if report:
        data = request.json
        report.govt_agency = data.get('govt_agency', report.govt_agency)
        report.county = data.get('county', report.county)
        report.location_url = data.get('location_url', report.location_url)
        report.title = data.get('title', report.title)
        report.description = data.get('description', report.description)
        report.media = data.get('media', report.media)
        report.status = data.get('status', report.status)
        db.session.commit()
        return jsonify({'message': 'Corruption report updated successfully'})
    return jsonify({'error': 'Corruption report not found'}), 404

@app.route('/corruption_reports/<int:report_id>', methods=['DELETE'])
def delete_corruption_report(report_id):
    report = CorruptionReport.query.get(report_id)
    if report:
        db.session.delete(report)
        db.session.commit()
        return jsonify({'message': 'Corruption report deleted successfully'})
    return jsonify({'error': 'Corruption report not found'}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)