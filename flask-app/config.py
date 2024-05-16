from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

class ApplicationConfig:
    SECRET_KEY =  os.environ['SECRET_KEY']

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost/ireporter-db'