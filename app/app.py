from flask import Flask
from blueprints.home import home as home_blueprint
from blueprints.admin import admin as admin_blueprint
from blueprints.raw import raw as raw_blueprint
from blueprints.interface import interface as interface_blueprint


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'would like not to have this but apparently i have to'

    app.register_blueprint(home_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(raw_blueprint)
    app.register_blueprint(interface_blueprint)

    return app
