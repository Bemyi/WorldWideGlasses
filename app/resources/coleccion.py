from flask import redirect, render_template, request, url_for, flash, session, jsonify
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
            taskId = getUserTaskByName("Planificación de colección", case_id)
            # Se le asigna la tarea al usuario que creó la colección
            assign_task(taskId)
            # Se finaliza la tarea
            # to-do
            # Cargar la variable en bonita
            coleccion_id = Coleccion.get_by_name(nombre).id
            set_bonita_variable(
                case_id, "coleccion_id", coleccion_id, "java.lang.Integer"
            )
            updateUserTask(taskId, "completed")
            taskId = getUserTaskByName("Seleccionar fecha de lanzamiento", case_id)
            assign_task(taskId)
            updateUserTask(taskId, "completed")
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
    print(response.json())
    case_id = response.json()["caseId"]
    print("Case ID:")
    print(case_id)
    return case_id


@login_required
def assign_task(taskId):
    """Se le asigna una tarea al usuario logeado"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/system/session/unusedId"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print(response)
    print(response.json()["user_id"])
    user_id = response.json()["user_id"]

    URL = "http://localhost:8080/bonita/API/bpm/humanTask/" + taskId
    headers = getBonitaHeaders()
    body = {"assigned_id": user_id}
    # Lo convierto a json porque sino tira 500
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)
    print(response)


@login_required
def updateUserTask(taskId, state):
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/userTask/" + taskId
    headers = getBonitaHeaders()
    body = {"state": state}
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)
    print(response)


@login_required
def set_bonita_variable(case_id, variable_name, variable_value, type):
    """setea un valor a la variable que es pasada por parametro"""
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
def getUserTaskByName(taskName, caseId):
    """Obtengo la tarea por su case y name para tener su id"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/userTask"
    headers = getBonitaHeaders()
    params = {"s": taskName, "caseId": caseId}
    response = requestSession.get(URL, headers=headers, params=params)
    print(response)
    print(response.json()[0]["id"])
    taskId = response.json()[0]["id"]
    return taskId


@login_required
def getBonitaHeaders():
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
        "Content-Type": "application/json",
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
    materiales_todos = Material.materiales()
    if session["current_rol"] == "Creativa":
        """Template Seleccionar materiales"""
        materiales = request.form.getlist("materiales[]")
        token = login_api_reservas()
        listado = listado_api_reservas(token, materiales)
        # filtramos materiales obtenidos
        mats_obtenidos = set()
        for e in listado:
            mats_obtenidos.add(e["name"])
        if not (set(materiales) == mats_obtenidos):
            materiales_faltan = set(materiales) - mats_obtenidos
            flash("Faltan los siguientes materiales: " + str(materiales_faltan))
            return render_template(
                "coleccion/seleccion_materiales.html", materiales=materiales_todos
            )
        return render_template("coleccion/reservar_materiales.html", materiales=listado)
    flash("Algo falló")
    return render_template(
        "coleccion/seleccion_materiales.html", materiales=materiales_todos
    )


@login_required
def login_api_reservas():
    requestSession = requests.Session()
    URL = "http://127.0.0.1:8000/login"
    # cambiar está hardcodeado
    body = {"username": "walter.bates", "password": "bpm"}
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    print(response)
    token = response.json()["token"]
    return token


@login_required
def listado_api_reservas(token, materiales):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:8000/materiales"
    body = {"names": materiales}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    listado = response.json()
    return listado


@login_required
def reservar_api_reservas(token, materiales):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:8000/reservar_materiales"
    body = {
        "materials": [
            {"id": 1, "quantity": 1},
            {"id": 2, "quantity": 1},
            {"id": 3, "quantity": 1},
        ],
        "user_id": 1,
        "colection_id": 1,
    }
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    listado = response.json()
    return listado


@login_required
def reservar_materiales():
    if session["current_rol"] == "Creativa":
        """Template Reservar materiales"""
        token = login_api_reservas()
        materiales = request.form.getlist("materiales[]")
        cantidades = request.form.getlist("cantidad[]")
        listado = []
        print(cantidades)
        print(materiales)
        for i in range(len(materiales)):
            listado.append({"id": materiales[i], "cantidad": cantidades[i]})
        print(listado)
        print(jsonify(listado))
        reservar_api_reservas(token, materiales)
    flash("No tienes permiso para acceder a este sitio")
    return redirect(url_for("home"))
