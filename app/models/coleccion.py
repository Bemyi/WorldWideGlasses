from app.db import db

# Login
from flask_login import UserMixin


class Coleccion(db.Model, UserMixin):
    __tablename__ = "coleccion"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    plazo_fabricacion = db.Column(db.DateTime)
    fecha_lanzamiento = db.Column(db.DateTime)
    tipos = db.relationship(
        "TipoDeModelo", secondary="coleccion_tipo", backref="coleccion"
    )
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    def __init__(
        self,
        name,
        plazo_fabricacion,
        fecha_lanzamiento,
    ):
        self.name = (name,)
        self.plazo_fabricacion = (plazo_fabricacion,)
        self.fecha_lanzamiento = fecha_lanzamiento

    def crear(name, plazo_fabricacion, fecha_lanzamiento):
        """Crea una coleccion"""
        coleccion = Coleccion(name, plazo_fabricacion, fecha_lanzamiento)
        db.session.add(coleccion)
        db.session.commit()
