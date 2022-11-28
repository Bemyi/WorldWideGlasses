from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp, Length, ValidationError
from app.models.tipo import Tipo


class FormAltaTipo(FlaskForm):

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

    def validate_nombre(form, tipoV):
        tipo = Tipo.get_by_name(tipoV.data)
        if tipo != None:
            raise ValidationError("Ya existe ese nombre para otro tipo")

    enviar = SubmitField("Guardar")
