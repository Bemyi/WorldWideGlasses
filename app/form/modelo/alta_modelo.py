from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp, Length

# from wtforms.fields.core import SelectField
from wtforms.fields.choices import SelectField


class FormAltaModelo(FlaskForm):

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
    descripcion = StringField(
        "Descripción",
        validators=[
            DataRequired(message="El campo descripción es obligatorio"),
            Regexp(
                "^[A-Za-záéíóúÁÉÍÓÚ ]*[A-Za-záéíóúÁÉÍÓÚ][A-Za-záéíóúÁÉÍÓÚ ]*$",
                message="El campo descripción solo puede contener letras",
            ),
            Length(
                min=2, max=140, message="El mínimo de caracteres es 2 y el máximo 140"
            ),
        ],
        default="",
    )
    tipo = SelectField(
        "Tipo",
        validators=[
            DataRequired(message="El campo tipo es obligatorio"),
            Regexp(
                "^[A-Za-z0-9áéíóúÁÉÍÓÚ ]*[A-Za-z0-9áéíóúÁÉÍÓÚ][A-Za-z0-9áéíóúÁÉÍÓÚ ]*$",
                message="El campo tipo solo puede contener letras y números",
            ),
        ],
        choices=["1", "2"],
    )
    enviar = SubmitField("Guardar")