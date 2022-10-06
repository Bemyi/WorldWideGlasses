from flask import redirect, render_template, request, url_for, flash, session
from flask_login import current_user, login_required
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.models.coleccion import Coleccion
import requests
import json

from app.models.modelo import Modelo


@login_required
def crear():
    """Creación de una nueva coleccion"""
    form = FormAltaColeccion()
    if form.validate_on_submit():
        nombre = form.nombre.data
        fecha_lanzamiento = form.fecha_lanzamiento.data
        modelos = request.form.getlist("modelos[]")
        Coleccion.crear(nombre, fecha_lanzamiento, current_user.id, modelos)
        # Se instancia la tarea
        case_id = init_process()
        # Se le asigna la tarea al usuario que creó la colección
        # assign_task()
        # Se finaliza la tarea
        # to-do
        # Cargar la variable en bonita
        coleccion_id = Coleccion.get_by_name(nombre).id
        set_bonita_variable(case_id, "coleccion_id", coleccion_id, "java.lang.Integer")
        flash("¡La colección fue creada con exito!")
        return redirect(url_for("home"))
    modelos = Modelo.modelos()
    return render_template("coleccion/nuevo.html", form=form, modelos=modelos)


@login_required
def init_process():
    # se le pega a la API y se recupera el id del proceso
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/process?s=Creación de colección"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    processId = response.json()[0]["id"]

    print("Response del get id del proceso:")
    print(response)
    print("Process ID: " + response.json()[0]["id"])

    # se instancia el proceso con su id, creando una tarea
    URL = "http://localhost:8080/bonita/API/bpm/process/" + processId + "/instantiation"
    headers = getBonitaHeaders()
    response = requestSession.post(URL, headers=headers)

    print("Response al instanciar proceso:")
    print(response)
    case_id = response.json()["caseId"]
    print("Case ID:")
    print(case_id)
    return case_id


# @login_required
# def assign_task():
#     requestSession = requests.Session()
#     URL = "http://localhost:8080/bonita/API/system/session/unusedId"
#     headers = getBonitaHeaders()
#     response = requestSession.get(URL, headers=headers)
#     print(response)
#     print(response.json()["user_id"])
#     user_id = response.json()["user_id"]

#     URL = "http://localhost:8080/bonita/API/bpm/activity/20006"
#     headers = getBonitaHeaders()
#     body = {"assigned_id": user_id}
#     response = requestSession.put(URL, headers=headers, data=body)
#     print(response)


@login_required
def set_bonita_variable(case_id, variable_name, variable_value, type):
    requestSession = requests.Session()
    URL = (
        "http://localhost:8080/bonita/API/bpm/caseVariable/"
        + str(case_id)
        + "/"
        + variable_name
    )
    body = {"value": variable_value, "type": type}
    headers = getBonitaHeaders()
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)
    print("Response de setear variable bonita:")
    print(response)
    response = requestSession.get(URL, headers=headers)
    print("Response al hacer get de variable bonita:")
    print(response)
    print("Valor de la variable coleccion_id:")
    print(response.json()["value"])


def getBonitaHeaders():
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    return headers


@login_required
def nuevo():
    """Template Nueva coleccion"""
    form = FormAltaColeccion()
    modelos = Modelo.modelos()
    return render_template("coleccion/nuevo.html", form=form, modelos=modelos)
