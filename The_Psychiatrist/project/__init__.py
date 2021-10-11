import sys
sys.path.append(sys.path[0]+'/project/lib')
import helper
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = helper.config["secret"]
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = helper.config["sql_alchemy_track_modifications"]
    app.config['SQLALCHEMY_DATABASE_URI'] = helper.config["sql_database_uri"]

    db.init_app(app)

    # blueprint for app
    from .app import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app