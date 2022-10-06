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
        ],
        choices=["1", "2"],
    )
    enviar = SubmitField("Guardar")
