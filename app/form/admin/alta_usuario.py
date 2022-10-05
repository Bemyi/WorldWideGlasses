from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Regexp, Length, EqualTo
from datetime import date

class FormAltaUsuario(FlaskForm):
    first_name = StringField('Nombre', validators=[
        DataRequired(message="El campo nombre es obligatorio"),
        Regexp(
            "^[A-Za-záéíóúÁÉÍÓÚñÑ ]*[A-Za-záéíóúÁÉÍÓÚñÑ][A-Za-záéíóúÁÉÍÓÚñÑ ]*$",
            message="El campo nombre solo puede contener letras",
        ),
        Length(
            min=2, max=40, message="El mínimo de caracteres es 2 y el máximo 40"
        ),
    ])
    last_name = StringField('Apellido', validators=[
        DataRequired(message="El campo apellido es obligatorio"),
        Regexp(
            "^[A-Za-záéíóúÁÉÍÓÚñÑ ]*[A-Za-záéíóúÁÉÍÓÚñÑ][A-Za-záéíóúÁÉÍÓÚñÑ ]*$",
            message="El campo nombre solo puede contener letras",
        ),
        Length(
            min=2, max=40, message="El mínimo de caracteres es 2 y el máximo 40"
        ),
    ])
    email = StringField('Email', validators=[
        DataRequired(message="El campo email es obligatorio"),
        Length(
            min=6, max=35, message="El mínimo de caracteres es 2 y el máximo 40"
        ),
    ])
    username = StringField('Nombre de usuario', validators=[
        DataRequired(message="El campo nombre de usuario es obligatorio"),
        Length(
            min=2, max=40, message="El mínimo de caracteres es 2 y el máximo 40"
        ),
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="El campo contraseña es obligatorio"),
        EqualTo('confirm', message="Las contraseñas deben coincidir"),
        Length(
            min=2, max=40, message="El mínimo de caracteres es 2 y el máximo 40"
        ),
    ])

    confirm = PasswordField('Repita la contraseña')

    enviar = SubmitField("Confirmar")