import os

from flask import Flask

from . import auth, bugs, db


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "bug-tracker-dev-secret"
    app.config["DATABASE"] = os.path.join(app.root_path, "..", "bugtracker.db")

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(bugs.bp)

    return app
