from app.db import db

# Login
from flask_login import UserMixin


class TipoDeModelo(db.Model, UserMixin):
    __tablename__ = "tipo_modelo"

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
