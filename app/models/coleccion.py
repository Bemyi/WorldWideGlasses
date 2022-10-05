from app.db import db

# Login
from flask_login import UserMixin

from app.models.modelo import Modelo

coleccion_tiene_modelo = db.Table(
    "coleccion_tiene_modelo",
    db.Column("coleccion_id", db.Integer, db.ForeignKey("coleccion.id"), primary_key=True),
    db.Column(
        "modelo_id",
        db.Integer,
        db.ForeignKey("modelo.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

class Coleccion(db.Model, UserMixin):
    __tablename__ = "coleccion"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    fecha_lanzamiento = db.Column(db.DateTime)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    # relacion Many-to-Many
    coleccion_tiene_modelo = db.relationship(
        "Modelo",
        secondary=coleccion_tiene_modelo,
        lazy="subquery",
        backref=db.backref("colecciones", lazy=True),
    )

    def __init__(
        self,
        name,
        fecha_lanzamiento,
        usuario_id,
        modelos
    ):
        self.name = name
        self.fecha_lanzamiento = fecha_lanzamiento
        self.usuario_id = usuario_id
        lista = []
        for modelo_id in modelos:
            lista.append(Modelo.query.get(modelo_id))
        self.coleccion_tiene_modelo = lista

    def crear(name, fecha_lanzamiento, usuario_id, modelos):
        """Crea una coleccion"""
        coleccion = Coleccion(name, fecha_lanzamiento, usuario_id, modelos)
        db.session.add(coleccion)
        db.session.commit()
    
    def get_by_name(name):
        return Coleccion.query.filter_by(name=name).first()
