from email import header
from flask import redirect, render_template, url_for, flash, session
from flask_login import login_required
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.models.coleccion import Coleccion
import requests
import json


@login_required
def crear():
    """Creación de una nueva coleccion"""
    form = FormAltaColeccion()
    if form.validate_on_submit():
        nombre = form.nombre.data
        plazo_fabricacion = form.plazo_fabricacion.data
        fecha_lanzamiento = form.fecha_lanzamiento.data
        Coleccion.crear(nombre, plazo_fabricacion, fecha_lanzamiento)
        flash("¡El usuario fue creado con exito!")
        return redirect(url_for("home"))
    return render_template("coleccion/nuevo.html", form=form)


@login_required
def portal_login(url, username, password):
    """Se logea y obtiene la cookie de bonita"""
    # http = httplib2.Http(disable_ssl_certificate_validation=disable_cert_validation)
    API = "/loginservice"
    URL = url + API
    body = {"username": username, "password": password, "redirect": "false"}
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    requestSession = requests.Session()
    response = requestSession.post(URL, data=body, headers=headers)
    session["JSESSION"] = "JSESSIONID=" + response.cookies.get("JSESSIONID")
    session["bonita_token"] = response.cookies.get("X-Bonita-API-Token")
    print(response)
    print(response.cookies.get("X-Bonita-API-Token"))


@login_required
def init_process():
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/process?s=prueba"
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    response = requestSession.get(URL, headers=headers)
    processId = response.json()[0]["id"]
    print(response.json()[0]["id"])
    print(response)
    URL = "http://localhost:8080/bonita/API/bpm/process/" + processId + "/instantiation"
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    response = requestSession.post(URL, headers=headers)
    print("Del iniciar proceso:")
    print(response)


@login_required
def assign_task():
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/system/session/unusedId"
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    response = requestSession.get(URL, headers=headers)
    print(response)
    print(response.json()["user_id"])
    user_id = response.json()["user_id"]
    URL = "http://localhost:8080/bonita/API/bpm/activity/20006"
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    body = {"assigned_id": user_id}
    response = requestSession.put(URL, headers=headers, data=body)
    print(response)


@login_required
def nuevo():
    """Template Nueva coleccion"""
    form = FormAltaColeccion()
    portal_login("http://localhost:8080/bonita", "walter.bates", "bpm")
    init_process()
    assign_task()
    return render_template("coleccion/nuevo.html", form=form)
