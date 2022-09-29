from flask_login import current_user
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.models.usuario import Usuario
from werkzeug.security import check_password_hash


def login():
    """Template de login. Si el usuario esta autenticado
    no puede volver a logearse"""
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("auth/login.html")


def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = Usuario.query.filter_by(email=email).first()

    # Chequeamos si existe el usuario
    # Chequeamos si la contraseña corresponde con la hasheada
    if not user or not check_password_hash(user.password, password):
        flash("El usuario y/o la contraseña son incorrectos.")
        return redirect(
            url_for("login")
        )  # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for("home"))


@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
