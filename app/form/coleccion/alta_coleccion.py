from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Regexp, Length
from datetime import date


class FormAltaColeccion(FlaskForm):

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El campo nombre es obligatorio"),
            Regexp(
                "^[A-Za-záéíóúÁÉÍÓÚ ]*[A-Za-záéíóúÁÉÍÓÚ][A-Za-záéíóúÁÉÍÓÚ ]*$",
                message="El campo nombre solo puede contener letras",
            ),
            Length(
                min=2, max=40, message="El mínimo de caracteres es 2 y el máximo 40"
            ),
        ],
        default="",
    )
    plazo_fabricacion = StringField(
        "plazo_fabricacion",
        default=date.today,
    )
    fecha_lanzamiento = DateField(
        "fecha_lanzamiento",
        default=date.today,
    )
    enviar = SubmitField("Guardar")
