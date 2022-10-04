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
        # Se instancia la tarea 
        init_process()
        # Se le asigna la tarea al usuario que creó la colección
        #assign_task()
        #Se finaliza la tarea
        flash("¡La colección fue creada con exito!")
        return redirect(url_for("home"))
    return render_template("coleccion/nuevo.html", form=form)

@login_required
def init_process():
    #se le pega a la API y se recupera el id del proceso
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/process?s=Creación de colección"
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    response = requestSession.get(URL, headers=headers)
    processId = response.json()[0]["id"]
    
    print("Get id del proceso:")
    print(response)
    print("Process ID: " + response.json()[0]["id"])
    
    #se instancia el proceso con su id, creando una tarea
    URL = "http://localhost:8080/bonita/API/bpm/process/" + processId + "/instantiation"
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    response = requestSession.post(URL, headers=headers)
    
    print("Instanciar proceso:")
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
    return render_template("coleccion/nuevo.html", form=form)
