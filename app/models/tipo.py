from app.db import db

# Login
from flask_login import UserMixin


class Tipo(db.Model, UserMixin):
    __tablename__ = "tipo"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    modelo = db.relationship("Modelo", backref="tipo", uselist=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    def __init__(
        self,
        name,
    ):
        self.name = name

    def crear(name):
        """Crea un tipo de anteojo"""
        tipo = Tipo(name)
        db.session.add(tipo)
        db.session.commit()

    def tipos():
        """Devuelve todos los tipos"""
        return Tipo.query.all()

    def get_by_name(name):
        return Tipo.query.filter_by(name=name).first()
