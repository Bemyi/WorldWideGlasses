from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Regexp, Length, ValidationError
from datetime import date, datetime
from app.models.coleccion import Coleccion


class FormAltaColeccion(FlaskForm):

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El campo nombre es obligatorio"),
            Length(
                min=2, max=40, message="El mínimo de caracteres es 2 y el máximo 40"
            ),
        ],
        default="",
    )

    def validate_nombre(form, nombreV):
        coleccion = Coleccion.get_by_name(nombreV.data)
        if coleccion != None:
            raise ValidationError("Ya existe ese nombre para otra colección")

    fecha_lanzamiento = DateField(
        "fecha_lanzamiento",
        default=date.today(),
        validators=[DataRequired()],
    )

    enviar = SubmitField("Guardar")

    def validate_fecha_lanzamiento(self, f):
        if f.data <= date.today():
            raise ValidationError(
                "La fecha de lanzamiento debe ser mayor a la fecha actual"
            )
