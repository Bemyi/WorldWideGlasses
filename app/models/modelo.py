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
    ):
        self.name = name
        self.descripcion = descripcion
