from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Regexp, Length
from datetime import date


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

    fecha_lanzamiento = DateField(
        "fecha_lanzamiento",
        default=date.today,
    )
    enviar = SubmitField("Guardar")
