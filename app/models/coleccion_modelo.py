from app.db import db

# Login
from flask_login import UserMixin


class Coleccion_Modelo(db.Model, UserMixin):
    __tablename__ = "coleccion_modelo"

    id = db.Column(db.Integer, primary_key=True)
    coleccion = db.Column("coleccion_id", db.Integer, db.ForeignKey("coleccion.id"))
    modelo = db.Column("modelo_id", db.Integer, db.ForeignKey("modelo.id"))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
