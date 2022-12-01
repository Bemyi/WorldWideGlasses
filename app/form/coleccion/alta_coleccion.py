from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange
from datetime import date, datetime, timedelta
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

    cantidad_lentes = IntegerField("Cantidad de lentes", validators=[NumberRange(min=1, max=999999, message="La cantidad de lentes debe ser mayor a 0"), DataRequired(message="El campo cantidad de lentes es obligatorio")])

    def validate_nombre(form, nombreV):
        coleccion = Coleccion.get_by_name(nombreV.data)
        if coleccion != None:
            raise ValidationError("Ya existe ese nombre para otra colección")

    fecha_lanzamiento = DateField(
        "fecha_lanzamiento",
        default=date.today() + timedelta(30),
        validators=[DataRequired()],
    )

    enviar = SubmitField("Guardar")

    def validate_fecha_lanzamiento(self, f):
        if f.data <= date.today() + timedelta(30):
            raise ValidationError(
                "La fecha de lanzamiento debe ser al menos 30 días posterior a la fecha actual"
            )
