from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, Regexp, Length
from datetime import date


class FormSeleccionarMateriales(FlaskForm):

    cantidad = IntegerField(
        "Cantidad",
        validators=[DataRequired(message="El campo cantidad es obligatorio")],
    )

    enviar = SubmitField("Guardar")
