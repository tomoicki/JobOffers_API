from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import environ as env
from dotenv import load_dotenv

load_dotenv()

host = env['PostgreSQL_host']
port = env['PostgreSQL_port']
user = env['PostgreSQL_user']
password = env['PostgreSQL_password']
db_name = env['PostgreSQL_db_name']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


