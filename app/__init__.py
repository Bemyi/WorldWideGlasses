import os
from os import environ
from flask import Flask, render_template
from app.db import db
from config import config

# Resources
from app.resources import auth
from app.resources import coleccion
from app.resources import tipo
from app.resources import modelo

# LoginManager
from flask_login import LoginManager, login_required
from flask_session import Session


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

    # Carga de la configuración
    env = environ.get("FLASK_ENV", "development")
    app.config.from_object(config[env])

    # Server Side session
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # Configure db
    db.init_app(app)
    with app.app_context():
        from app.models.usuario import Usuario
        from app.models.tipo import Tipo
        from app.models.modelo import Modelo
        from app.models.coleccion import Coleccion

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

    # Autenticación
    app.add_url_rule("/login", "login", auth.login)
    app.add_url_rule("/login", "login_auth", auth.login_post, methods=["POST"])
    app.add_url_rule("/logout", "logout", auth.logout)

    # Ruta para el Home (usando decorator)
    @app.route("/")
    @login_required
    def home():
        return render_template("home.html")

    # Ruta de colecciones
    app.add_url_rule("/coleccion/nueva", "nueva_coleccion", coleccion.nuevo)
    app.add_url_rule(
        "/coleccion/crear", "crear_coleccion", coleccion.crear, methods=["POST"]
    )

    ## Ruta de materiales
    app.add_url_rule(
        "/coleccion/reservar_materiales",
        "reservar_materiales",
        coleccion.reservar_materiales,
        methods=["POST"],
    )
    app.add_url_rule(
        "/coleccion/seleccionar_materiales",
        "seleccionar_materiales",
        coleccion.seleccionar_materiales,
    )
    app.add_url_rule(
        "/coleccion/seleccion_materiales",
        "seleccion_materiales",
        coleccion.seleccion_materiales,
        methods=["POST"],
    )

    # Ruta de tipo
    app.add_url_rule("/tipo/nuevo", "nuevo_tipo", tipo.nuevo)
    app.add_url_rule("/tipo/crear", "crear_tipo", tipo.crear, methods=["POST"])

    # Ruta de modelo
    app.add_url_rule("/modelo/nuevo", "nuevo_modelo", modelo.nuevo)
    app.add_url_rule("/modelo/crear", "crear_modelo", modelo.crear, methods=["POST"])

    return app
