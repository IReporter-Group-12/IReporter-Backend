from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/ireporter-db'

db.init_app(app)
migrate= Migrate(app, db)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)