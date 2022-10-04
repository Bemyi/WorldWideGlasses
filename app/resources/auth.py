from flask_login import current_user
from flask import render_template, redirect, session, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.models.usuario import Usuario
from werkzeug.security import check_password_hash
import requests
# Password de Walter
from werkzeug.security import generate_password_hash

def login():
    """Template de login. Si el usuario esta autenticado
    no puede volver a logearse"""
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    pass_walter = generate_password_hash("bpm", "sha256")
    flash("La contraseña de Walter es: " + pass_walter)
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

    # chequeamos si el usuario existe en la organización de bonita
    response = portal_login("http://localhost:8080/bonita", user.username, password)
    if response.status_code!=204:
        flash("El usuario no forma parte de la organización.")
        return redirect(
            url_for("login")
        ) 

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)   
    return redirect(url_for("home"))


@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

def portal_login(url, username, password):
    """Se logea y obtiene la cookie de bonita"""
    # http = httplib2.Http(disable_ssl_certificate_validation=disable_cert_validation)
    print("Usuario: "+username)
    print("Pass: "+password)
    API = "/loginservice"
    URL = url + API
    body = {"username": username, "password": password, "redirect": "false"}
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    requestSession = requests.Session()
    response = requestSession.post(URL, data=body, headers=headers)
    print(response)
    # si todo sale bien seteo las variables de sesión
    if response.status_code==204:
        session["JSESSION"] = "JSESSIONID=" + response.cookies.get("JSESSIONID")
        session["bonita_token"] = response.cookies.get("X-Bonita-API-Token")
        
        print("Login Bonita:")
        print(response)
        print("Bonita-Api-Token: " + response.cookies.get("X-Bonita-API-Token"))

    # devuelvo la respuesta para saber si puedo loguearme o no
    return response