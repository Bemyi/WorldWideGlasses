from app.db import db

# Login
from flask_login import UserMixin


class Material(db.Model, UserMixin):
    __tablename__ = "material"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
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
        """Crea un material"""
        material = Material(name)
        db.session.add(material)
        db.session.commit()

    def materiales():
        """Devuelve todos los materiales"""
        return Material.query.all()
