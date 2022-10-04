from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp, Length


class FormAltaTipo(FlaskForm):

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
    enviar = SubmitField("Guardar")
