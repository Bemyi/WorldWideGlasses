from app.db import db

# Login
from flask_login import UserMixin


class Tarea(db.Model, UserMixin):
    __tablename__ = "tarea"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True)
    descripcion = db.Column(db.String(255), unique=True)
    fecha_limite = db.Column(db.DateTime)
    coleccion_id = db.Column(db.Integer, db.ForeignKey("coleccion.id"), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    def __init__(
        self,
        nombre,
        descripcion,
        fecha_limite,
        coleccion_id
    ):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_limite = fecha_limite
        self.coleccion_id = coleccion_id

    def crear(nombre, descripcion, fecha_limite, coleccion_id):
        """Crea una tarea"""
        tarea = Tarea(nombre, descripcion, fecha_limite, coleccion_id)
        db.session.add(tarea)
        db.session.commit()

    def eliminar(self):
        """Elimina una tarea"""
        db.session.delete(self)
        db.session.commit()

    def tareas():
        """Devuelve todos los tareas"""
        return Tarea.query.all()

    def get_by_name(nombre):
        return Tarea.query.filter_by(nombre=nombre).first()

    def get_by_name_and_coleccion(nombre, coleccion_id):
        return Tarea.query.filter_by(nombre=nombre, coleccion_id=coleccion_id).first()

    def get_by_id(id):
        return Tarea.query.filter_by(id=id).first()

    def get_by_coleccion_id(coleccion_id):
        return Tarea.query.filter_by(coleccion_id=coleccion_id).all()