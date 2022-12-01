from app.db import db

# Login
from flask_login import UserMixin


class Sede(db.Model, UserMixin):
    __tablename__ = "sede"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    coleccion_sede = db.relationship("Coleccion_sede", backref="sede", uselist=False)

    def __init__(
        self,
        name,
    ):
        self.name = name

    def crear(name):
        """Crea una sede"""
        sede = Sede(name)
        db.session.add(sede)
        db.session.commit()

    def sedes():
        """Devuelve todas las sedes"""
        return Sede.query.all()

    def get_by_name(name):
        return Sede.query.filter_by(name=name).first()

    def get_by_id(id):
        return Sede.query.filter_by(id=id).first()