from app.db import db

# Login
from flask_login import UserMixin


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))

    def __init__(
        self,
        email,
        username,
        first_name,
        last_name,
        password,
    ):
        self.email = email
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.password = password

    def crear(email, username, first_name, last_name, password):
        """Crea un usuario"""
        user = Usuario(email, username, first_name, last_name, password)
        db.session.add(user)
        db.session.commit()
