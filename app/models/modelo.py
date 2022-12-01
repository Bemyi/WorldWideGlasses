from app.db import db

# Login
from flask_login import UserMixin


class Modelo(db.Model, UserMixin):
    __tablename__ = "modelo"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    tipo_id = db.Column(db.Integer, db.ForeignKey("tipo.id"), nullable=False)
    descripcion = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    def __init__(
        self,
        name,
        descripcion,
        tipo_id,
    ):
        self.name = name
        self.descripcion = descripcion
        self.tipo_id = tipo_id

    def crear(name, descripcion, tipo):
        """Crea un modelo"""
        modelo = Modelo(name, descripcion, tipo)
        db.session.add(modelo)
        db.session.commit()

    def modelos():
        """Devuelve todos los tipos"""
        return Modelo.query.all()

    def get_by_name(name):
        return Modelo.query.filter_by(name=name).first()

    def get_by_id(id):
        return Modelo.query.filter_by(id=id).first()
