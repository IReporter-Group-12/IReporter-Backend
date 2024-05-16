from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from models import db, PublicPetition, PetitionResolution


app = Flask(__name__)
app.config.from_object(ApplicationConfig)
CORS(app)
db.init_app(app)
migrate= Migrate(app, db)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return "Welcome to Intervention Records"

@app.route('/public_petitions', methods=['GET', 'POST'])
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
            location_url=request.form.get("location_url"),
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