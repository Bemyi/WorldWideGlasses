from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp, Length, ValidationError
from app.models.modelo import Modelo


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

    def validate_nombre(form, modeloV):
        modelo = Modelo.get_by_name(modeloV.data)
        if modelo != None:
            raise ValidationError("Ya existe ese nombre para otro modelo")

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
    enviar = SubmitField("Guardar")
