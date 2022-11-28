from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, ValidationError
from datetime import date, timedelta
from app.models.coleccion import Coleccion


class FormReprogramarColeccion(FlaskForm):

    fecha_lanzamiento = DateField(
        "fecha_lanzamiento",
        validators=[DataRequired()],
    )

    enviar = SubmitField("Guardar")

    def validate_fecha_lanzamiento(self, f):
        if f.data <= date.today() + timedelta(30):
            raise ValidationError(
                "La fecha de lanzamiento debe ser al menos 30 días posterior a la fecha actual"
            )
