from flask_login import current_user
from flask import render_template, redirect, session, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.models.coleccion import Coleccion
from app.models.usuario import Usuario
import requests

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
    if not user or user.password != password:
        flash("El usuario y/o la contraseña son incorrectos.")
        return redirect(
            url_for("login")
        )  # if user doesn't exist or password is wrong, reload the page

    # chequeamos si el usuario existe en la organización de bonita
    response = portal_login(user.username, password)
    if response.status_code != 204:
        flash("El usuario no forma parte de la organización.")
        return redirect(url_for("login"))
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    session["current_rol"] = getUserMembership()
    return redirect(url_for("home"))


@login_required
def logout():
    # logout de bonita
    portal_logout()
    logout_user()
    return redirect(url_for("login"))


def portal_login(username, password):
    """Se logea y obtiene la cookie de bonita"""
    URL = "http://localhost:8080/bonita/loginservice"
    body = {"username": username, "password": password, "redirect": "false"}
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    requestSession = requests.Session()
    response = requestSession.post(URL, data=body, headers=headers)
    print("Response del login:")
    print(response)
    # si todo sale bien seteo las variables de sesión
    if response.status_code == 204:
        session["JSESSION"] = "JSESSIONID=" + response.cookies.get("JSESSIONID")
        session["bonita_token"] = response.cookies.get("X-Bonita-API-Token")
        print("Bonita-Api-Token: " + response.cookies.get("X-Bonita-API-Token"))
        print("JSESSIONID: " + response.cookies.get("JSESSIONID"))
    # devuelvo la respuesta para saber si puedo loguearme o no
    return response


@login_required
def portal_logout():
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/logoutservice"
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    response = requestSession.get(URL, headers=headers)
    print("Response de logout Bonita:")
    print(response)


@login_required
def getUserMembership():
    requestSession = requests.Session()
    user = getLoggedUser()
    params = {"f": "user_id=" + user["id"], "d": "role_id"}
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    URL = "http://localhost:8080/bonita/API/identity/membership"
    response = requestSession.get(URL, headers=headers, params=params)
    print("Response de getUserMemebership:")
    print(response)
    print("rol:")
    print(response.json()[0]["role_id"]["name"])
    return response.json()[0]["role_id"]["name"]


@login_required
def getLoggedUser():
    requestSession = requests.Session()
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    URL = "http://localhost:8080/bonita/API/system/session/unusedid"
    response = requestSession.get(URL, headers=headers)
    print("Response de getLoggedUser:")
    print(response)
    print("username: " + response.json()["user_name"])
    return {
        "id": response.json()["user_id"],
        "username": response.json()["user_name"],
    }
