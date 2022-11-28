from datetime import timedelta
import time
from flask import redirect, render_template, request, url_for, flash, session, jsonify
from flask_login import current_user, login_required
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.form.coleccion.seleccionar_materiales import FormSeleccionarMateriales
from app.models.coleccion import Coleccion
import requests
import json

from app.models.modelo import Modelo
from app.models.material import Material

import gspread
from oauth2client.service_account import ServiceAccountCredentials


@login_required
def crear():
    """Creación de una nueva coleccion"""
    if session["current_rol"] == "Creativa":
        form = FormAltaColeccion()
        if form.validate_on_submit():
            nombre = form.nombre.data
            fecha_lanzamiento = form.fecha_lanzamiento.data
            modelos = request.form.getlist("modelos[]")
            # Se instancia la tarea
            case_id = init_process()
            time.sleep(5)
            taskId = getUserTaskByName("Planificación de colección", case_id)
            # Se le asigna la tarea al usuario que creó la colección
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            time.sleep(5)
            # Se asigna la tarea 'Seleccionar fecha de lanzamiento'
            taskId = getUserTaskByName("Seleccionar fecha de lanzamiento", case_id)
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            # Si todo salió bien se crea la colección
            # resto un mes para setear fecha entrega y mando vacio para los modelos
            Coleccion.crear(
                case_id,
                nombre,
                fecha_lanzamiento,
                fecha_lanzamiento - timedelta(30),
                [1,2,3],
                "",
                modelos,
            )
            # Cargar las variables en bonita
            coleccion = Coleccion.get_by_name(nombre)

            set_bonita_variable(
                case_id, "materiales_disponibles", "false", "java.lang.Boolean"
            )
            set_bonita_variable(
                case_id, "coleccion_id", coleccion.id, "java.lang.Integer"
            )

            # Carga de la colección en el drive
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive",
            ]

            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "app/resources/client_secret.json",
                scope,
            )

            client = gspread.authorize(creds)

            sheet = client.open("Prueba").sheet1

            modelos = ""
            for index, m in enumerate(coleccion.coleccion_tiene_modelo):
                if index == len(coleccion.coleccion_tiene_modelo) - 1:
                    modelos = modelos + "- " + m.name + " (" + m.tipo.name + ")"
                else:
                    modelos = modelos + "- " + m.name + " (" + m.tipo.name + ") \n"

            usuarios = ""
            for index, u in enumerate(coleccion.coleccion_tiene_usuario):
                if index == len(coleccion.coleccion_tiene_usuario) - 1:
                    usuarios = usuarios + "- " + u.username
                else:
                    usuarios = usuarios + "- " + u.username + "\n"
            row = [
                coleccion.name,
                str(coleccion.fecha_lanzamiento),
                str(coleccion.fecha_entrega),
                modelos,
                usuarios
            ]
            index = len(sheet.get_all_values()) + 1
            sheet.insert_row(row, index)

            flash("¡La colección fue creada con exito!", "success")
            return redirect(url_for("home"))
        else:
            modelos = Modelo.modelos()
            return render_template("coleccion/nuevo.html", form=form, modelos=modelos)
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def init_process():
    # se le pega a la API y se recupera el id del proceso
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/process?s=Creación de colección"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response del get id del proceso:")
    print(response)
    if response.status_code == 200:
        processId = response.json()[0]["id"]
        print("Process ID: " + response.json()[0]["id"])

        # se instancia el proceso con su id, creando una tarea
        URL = (
            "http://localhost:8080/bonita/API/bpm/process/"
            + processId
            + "/instantiation"
        )
        headers = getBonitaHeaders()
        response = requestSession.post(URL, headers=headers)

        print("Response al instanciar proceso:")
        print(response)
        print(response.json())
        case_id = response.json()["caseId"]
        print("Case ID:")
        print(case_id)
        return case_id
    else:
        print("Entro al else")
        return redirect(url_for("logout"))  # esto no anda!!!


@login_required
def get_user_id():
    """Se recupera el id del usuario logeado"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/system/session/unusedId"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print(response)
    print(response.json()["user_id"])
    user_id = response.json()["user_id"]
    return user_id


@login_required
def assign_task(taskId):
    """Se le asigna una tarea al usuario logeado"""
    requestSession = requests.Session()
    user_id = get_user_id()
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
    print("Response del get user task:")
    print(response)
    print(response.json())
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
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def seleccionar_materiales(id_coleccion):
    if session["current_rol"] == "Operaciones":
        """Template Seleccionar materiales"""
        materiales = Material.materiales()
        return render_template(
            "coleccion/seleccion_materiales.html",
            materiales=materiales,
            id_coleccion=id_coleccion,
        )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def seleccion_materiales(id_coleccion):
    materiales_todos = Material.materiales()
    if session["current_rol"] == "Operaciones":
        """Template Seleccionar materiales"""
        materiales = request.form.getlist("materiales[]")
        token = login_api_reservas()
        listado = listado_api_reservas(token, materiales)
        # filtramos materiales obtenidos
        mats_obtenidos = [material["name"] for material in listado]
        # filtramos stocks para utilizarlos mas adelante
        stocks = [material["stock"] for material in listado]
        if not (set(materiales) == set(mats_obtenidos)):
            materiales_faltan = [i for i in materiales if i not in mats_obtenidos]
            flash("Faltan los siguientes materiales: " + str(materiales_faltan), "error")
            return render_template(
                "coleccion/seleccion_materiales.html",
                materiales=materiales_todos,
                id_coleccion=id_coleccion,
            )
        return render_template(
            "coleccion/guardar_materiales.html",
            materiales=listado,
            stocks=stocks,
            id_coleccion=id_coleccion,
            fecha_entrega=Coleccion.get_by_id(id_coleccion).fecha_entrega,
        )
    flash("Algo falló", "error")
    return render_template(
        "coleccion/seleccion_materiales.html", materiales=materiales_todos
    )


@login_required
def login_api_reservas():
    requestSession = requests.Session()
    URL = "http://127.0.0.1:8000/login"
    body = {"username": current_user.username, "password": current_user.password}
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
def reservar_api_reservas(token, materiales, id_coleccion):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:8000/reservar_materiales"
    body = {
        "materials": materiales,
        "user_id": int(get_user_id()),
        "colection_id": int(id_coleccion),
    }
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    print(data)
    response = requestSession.put(URL, data=data, headers=headers)
    listado = response.json()
    print(response)
    print(listado)
    return listado


@login_required
def guardar_materiales(id_coleccion):
    if session["current_rol"] == "Operaciones":
        """Template Reservar materiales"""
        token = login_api_reservas()
        materiales = eval(
            request.form.getlist("materiales[]")[0]
        )  # uso eval para volverlo dict
        stocks = eval(
            request.form.getlist("stocks[]")[0]
        )  # uso eval para volverlo dict
        cantidades = request.form.getlist("cantidad[]")
        print(stocks)
        listado = []
        for i in range(len(materiales)):
            if cantidades[i] != "0":
                if int(cantidades[i]) > stocks[i]:
                    flash("Stock insuficiente", "error")
                    return render_template(
                        "coleccion/guardar_materiales.html",
                        materiales=materiales,
                        stocks=stocks,
                        id_coleccion=id_coleccion,
                        fecha_entrega=Coleccion.get_by_id(id_coleccion).fecha_entrega,
                    )
                else:
                    listado.append(
                        {"id": materiales[i]["id"], "quantity": int(cantidades[i])}
                    )
        print(listado)
        Coleccion.get_by_id(id_coleccion).save_materials(str(listado))
        set_bonita_variable(
            Coleccion.get_by_id(id_coleccion).case_id,
            "materiales_fecha",
            "true",
            "java.lang.Boolean",
        )
        time.sleep(5)
        taskId = getUserTaskByName(
            "Consulta de materiales a la API", Coleccion.get_by_id(id_coleccion).case_id
        )
        assign_task(taskId)
        # Se finaliza la tarea
        updateUserTask(taskId, "completed")
        time.sleep(5)
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def reprogramar(id_coleccion):
    if session["current_rol"] == "Creativa":
        time.sleep(5)
        taskId = getUserTaskByName(
            "Consulta de materiales a la API", Coleccion.get_by_id(id_coleccion).case_id
        )
        assign_task(taskId)
        # Se finaliza la tarea
        updateUserTask(taskId, "completed")
        taskId = getUserTaskByName(
            "Planificación de distribución", Coleccion.get_by_id(id_coleccion).case_id
        )
        assign_task(taskId)
        # Se finaliza la tarea
        updateUserTask(taskId, "completed")
        time.sleep(5)
        return render_template(
            "coleccion/reprogramar.html",
            id_coleccion=id_coleccion,
        )
    else:
       flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def modificar_fecha(id_coleccion):
    if session["current_rol"] == "Creativa":
        nueva_fecha = request.form.get("fecha_lanzamiento")
        coleccion = Coleccion.get_by_id(id_coleccion)
        print(nueva_fecha)
        coleccion.modificar_lanzamiento(nueva_fecha)
        taskId = getUserTaskByName("Seleccionar fecha de lanzamiento", coleccion.case_id)
        assign_task(taskId)
        # Se finaliza la tarea
        updateUserTask(taskId, "completed")
        # calcular_fecha_entrega(coleccion)
        time.sleep(5)
        coleccion.modificar_entrega(coleccion.fecha_lanzamiento - timedelta(30))
        return redirect(url_for("home"))
    else:
       flash("danger_msg", "No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))
