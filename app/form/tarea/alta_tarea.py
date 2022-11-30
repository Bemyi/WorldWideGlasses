from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Regexp, Length, ValidationError
from datetime import date
from app.models.tarea import Tarea


class FormAltaTarea(FlaskForm):
    fin_fabricacion = DateField()
    id_coleccion = IntegerField()

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

    def validate_nombre(self, nombreV):
        tarea = Tarea.get_by_name_and_coleccion(nombreV.data, self.id_coleccion)
        if tarea != None:
            raise ValidationError("Ya existe ese nombre para otra tarea de esta colección")

    descripcion = StringField(
        "Descripción",
        validators=[
            DataRequired(message="El campo descripción es obligatorio"),
            Length(
                min=2, max=60, message="El mínimo de caracteres es 2 y el máximo 60"
            ),
        ],
        default="",
    )

    fecha_limite = DateField(
        "Fecha Límite",
        default=date.today(),
        validators=[DataRequired(message="El campo fecha límite es obligatorio")],
    )

    enviar = SubmitField("Guardar")

    def validate_fecha_limite(self, f):
        if f.data > self.fin_fabricacion.date():
            raise ValidationError(
                "La fecha limite debe ser anterior o igual a la fecha de fin del espacio de fabricación"
            )