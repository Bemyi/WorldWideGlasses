from flask import redirect, render_template, request, url_for, flash, session
from flask_login import current_user, login_required
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.form.coleccion.seleccionar_materiales import FormSeleccionarMateriales
from app.models.coleccion import Coleccion
import requests
import json

from app.models.modelo import Modelo
from app.models.material import Material


@login_required
def crear():
    """Creación de una nueva coleccion"""
    if session["current_rol"] == "Creativa":
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
            set_bonita_variable(
                case_id, "coleccion_id", coleccion_id, "java.lang.Integer"
            )
            flash("¡La colección fue creada con exito!")
            return redirect(url_for("home"))
        modelos = Modelo.modelos()
        return render_template("coleccion/nuevo.html", form=form, modelos=modelos)
    flash("No tienes permiso para acceder a este sitio")
    return redirect(url_for("home"))


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


@login_required
def getBonitaHeaders():
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
    }
    return headers


@login_required
def nuevo():
    if session["current_rol"] == "Creativa":
        """Template Nueva coleccion"""
        form = FormAltaColeccion()
        modelos = Modelo.modelos()
        return render_template("coleccion/nuevo.html", form=form, modelos=modelos)
    flash("No tienes permiso para acceder a este sitio")
    return redirect(url_for("home"))


@login_required
def seleccionar_materiales():
    if session["current_rol"] == "Creativa":
        """Template Seleccionar materiales"""
        materiales = Material.materiales()
        return render_template(
            "coleccion/seleccion_materiales.html", materiales=materiales
        )
    flash("No tienes permiso para acceder a este sitio")
    return redirect(url_for("home"))


@login_required
def seleccion_materiales():
    if session["current_rol"] == "Creativa":
        """Template Seleccionar materiales"""
        materiales = request.form.getlist("materiales[]")
        print("AAAAAAAAAA")
        requestSession = requests.Session()
        URL = "http://127.0.0.1:8000/login"
        body = {"username": "mario", "password": "123"}
        response = requestSession.get(URL, data=body)
        print(response)
        flash("¡Los materiales fueron seleccionados con exito!")
        return redirect(url_for("home"))
    flash("Algo falló")
    materiales = Material.materiales()
    return render_template("coleccion/seleccion_materiales.html", materiales=materiales)


# @login_required
# def reservar_materiales():
#     if session["current_rol"] == "Creativa":
#         """Template Reservar materiales"""
#         form = FormSeleccionarMateriales()
#         materiales = request.form.getlist("materiales[]")
#         print(materiales)
#         cantidades = request.form.getlist("cantidades[]")
#         print(cantidades)
#         x = len(materiales)
#         while x != 0:
#             print(cantidades[x - 1])
#             x = x - 1
#         return redirect(url_for("home"))
#     flash("No tienes permiso para acceder a este sitio")
#     return redirect(url_for("home"))
