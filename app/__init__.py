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
from app.resources import reservas
from app.resources import tarea
from app.resources import metrica

# LoginManager
from flask_login import LoginManager, login_required
from flask_session import Session
from app.helpers.bonita_api import get_completed_tasks_by_name, get_ready_tasks


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
        from app.models.sede import Sede
        from app.models.coleccion_sede import Coleccion_sede

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

    app.jinja_env.globals.update(
        get_ready_tasks=get_ready_tasks,
        get_completed_tasks_by_name=get_completed_tasks_by_name,
    )

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
    app.add_url_rule(
        "/coleccion/<id_coleccion>/reprogramar",
        "reprogramar_coleccion",
        coleccion.reprogramar,
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/modificar_fecha",
        "modificar_fecha_coleccion",
        coleccion.modificar_fecha,
        methods=["POST"],
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/planificar",
        "planificar_fabricacion",
        coleccion.planificar_fabricacion,
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/elaborar_plan",
        "elaborar_plan",
        coleccion.elaborar_plan,
        methods=["POST"],
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/administrar_tareas",
        "administrar_tareas",
        coleccion.administrar_tareas,
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/eliminar_coleccion",
        "eliminar_coleccion",
        coleccion.eliminar_coleccion,
        methods=["GET", "DELETE"],
    )

    # Ruta de tareas
    app.add_url_rule(
        "/coleccion/<id_coleccion>/crear",
        "crear_tarea",
        tarea.crear_tarea,
        methods=["POST"],
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/<id_tarea>/eliminar",
        "eliminar_tarea",
        tarea.eliminar_tarea,
        methods=["GET", "POST", "DELETE"],
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/<id_tarea>/finalizar",
        "finalizar_tarea",
        tarea.finalizar_tarea,
        methods=["GET", "POST"],
    )

    # Ruta de materiales
    app.add_url_rule(
        "/coleccion/<id_coleccion>/guardar_materiales",
        "guardar_materiales",
        reservas.guardar_materiales,
        methods=["POST"],
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/seleccionar_materiales",
        "seleccionar_materiales",
        reservas.seleccionar_materiales,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/seleccion_materiales",
        "seleccion_materiales",
        reservas.seleccion_materiales,
        methods=["POST"],
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/recibir_materiales",
        "recibir_materiales",
        reservas.recibir_materiales,
        methods=["GET", "POST"],
    )

    # Ruta de espacios de fabricacion
    app.add_url_rule(
        "/coleccion/<id_coleccion>/seleccionar_espacio",
        "seleccionar_espacio",
        reservas.seleccionar_espacio,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/reservar_espacio",
        "reservar_espacio",
        reservas.reservar_espacio,
        methods=["POST"],
    )

    # Ruta de planificación de distribución
    app.add_url_rule(
        "/coleccion/<id_coleccion>/nueva_distribucion",
        "nueva_distribucion",
        coleccion.nueva_distribucion,
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/planificar_distribucion",
        "planificar_distribucion",
        coleccion.planificar_distribucion,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/coleccion/<id_coleccion>/ver_lotes",
        "ver_lotes",
        coleccion.ver_lotes,
    )
    app.add_url_rule(
        "/coleccion/<id_lote>/enviar_lote",
        "enviar_lote",
        coleccion.enviar_lote,
        methods=["GET", "POST"],
    )

    # Ruta de tipo
    app.add_url_rule("/tipo/nuevo", "nuevo_tipo", tipo.nuevo)
    app.add_url_rule("/tipo/crear", "crear_tipo", tipo.crear, methods=["POST"])

    # Ruta de modelo
    app.add_url_rule("/modelo/nuevo", "nuevo_modelo", modelo.nuevo)
    app.add_url_rule("/modelo/crear", "crear_modelo", modelo.crear, methods=["POST"])

    # Ruta de metricas
    app.add_url_rule("/metrica", "metrica_index", metrica.index)

    return app
