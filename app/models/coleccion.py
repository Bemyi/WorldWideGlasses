from app.db import db
import requests
from flask import session
# Login
from flask_login import UserMixin

from app.models.modelo import Modelo

coleccion_tiene_modelo = db.Table(
    "coleccion_tiene_modelo",
    db.Column("coleccion_id", db.Integer, db.ForeignKey("coleccion.id"), primary_key=True),
    db.Column(
        "modelo_id",
        db.Integer,
        db.ForeignKey("modelo.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

class Coleccion(db.Model, UserMixin):
    __tablename__ = "coleccion"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer)
    name = db.Column(db.String(255), unique=True)
    fecha_lanzamiento = db.Column(db.DateTime)
    fecha_entrega = db.Column(db.DateTime)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    materiales = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    # relacion Many-to-Many
    coleccion_tiene_modelo = db.relationship(
        "Modelo",
        secondary=coleccion_tiene_modelo,
        lazy="subquery",
        backref=db.backref("colecciones", lazy=True),
    )

    def __init__(
        self,
        case_id,
        name,
        fecha_lanzamiento,
        fecha_entrega,
        usuario_id,
        materiales,
        modelos
    ):
        self.case_id = case_id
        self.name = name
        self.fecha_lanzamiento = fecha_lanzamiento
        self.fecha_entrega = fecha_entrega
        self.usuario_id = usuario_id
        self.materiales = materiales
        lista = []
        for modelo_id in modelos:
            lista.append(Modelo.query.get(modelo_id))
        self.coleccion_tiene_modelo = lista

    def crear(case_id, name, fecha_lanzamiento, fecha_entrega, usuario_id, materiales, modelos):
        """Crea una coleccion"""
        coleccion = Coleccion(case_id, name, fecha_lanzamiento, fecha_entrega, usuario_id, materiales, modelos)
        db.session.add(coleccion)
        db.session.commit()
    
    def get_by_name(name):
        return Coleccion.query.filter_by(name=name).first()
        
    def get_by_id(id):
        return Coleccion.query.filter_by(id=id).first()

    def get_ready_tasks(self, case_id):
        print(case_id)
        requestSession = requests.Session()
        URL = "http://localhost:8080/bonita/API/bpm/userTask?c=10&p=0&f="+str(case_id)+"caseId=1&f=state=ready"
        headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
        "Content-Type": "application/json",
        }
        params = {}
        response = requestSession.get(URL, headers=headers, params=params)
        print("Response del get tareas:")
        tareas = ([task['name'] for task in response.json()])
        print(tareas)
        return(tareas)

    def save_materials(self, materiales):
        """Guarda la lista temporal de materiales a reservar"""
        self.materiales = materiales
        db.session.commit()

    def delete_materials(self):
        """Borra la lista temporal de materiales a reservar"""
        self.materiales = ""
        db.session.commit()

    def modificar_lanzamiento(self, nueva_fecha):
            """Borra la lista temporal de materiales a reservar"""
            self.fecha_lanzamiento = nueva_fecha
            db.session.commit()