import os

from flask import Flask
from app.db import db
from app.resources import auth

# LoginManager
from flask_login import LoginManager


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Configure db
    db.init_app(app)
    with app.app_context():
        from app.models.usuario import Usuario

        db.create_all()

    # LoginManager Config
    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.login_message = "Inicie sesion para acceder a este sitio"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return Usuario.query.get(int(user_id))

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    # Autenticación
    app.add_url_rule("/login", "login", auth.login)
    app.add_url_rule("/login", "login_auth", auth.login_post, methods=["POST"])
    app.add_url_rule("/logout", "logout", auth.logout)
    return app
