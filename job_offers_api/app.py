from flask import Flask
from job_offers_api.blueprints.home import home as home_blueprint
from job_offers_api.blueprints.admin import admin as admin_blueprint
from job_offers_api.blueprints.raw import raw as raw_blueprint
from job_offers_api.blueprints.interface import interface as interface_blueprint


def create_app():
    app = Flask(__name__, template_folder='Templates')
    app.config['SECRET_KEY'] = 'would like not to have this but apparently i have to'

    app.register_blueprint(home_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(raw_blueprint)
    app.register_blueprint(interface_blueprint)

    return app
