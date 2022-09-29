from app.db import db

# Login
from flask_login import UserMixin


class Coleccion_TipoDeModelo(db.Model, UserMixin):
    __tablename__ = "coleccion_tipo"

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255))
    coleccion = db.Column("coleccion_id", db.Integer, db.ForeignKey("coleccion.id"))
    tipo_modelo = db.Column("tipo_id", db.Integer, db.ForeignKey("tipo_modelo.id"))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    def __init__(
        self,
        descripcion,
    ):
        self.descripcion = descripcion
