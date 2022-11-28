import time
from flask import redirect, render_template, url_for, flash, session, request
from flask_login import login_required, current_user
import requests
import json
from app.models.coleccion import Coleccion
from app.resources import coleccion


@login_required
def reservar_espacio(id_coleccion):
    """Se reserva un espacio"""
    # cambiar a operaciones
    if session["current_rol"] == "Operaciones":
        case_id = Coleccion.get_by_id(id_coleccion).case_id
        time.sleep(5)
        taskId = coleccion.getUserTaskByName(
            "Consultar espacio de fabricación",
            case_id,
        )
        coleccion.set_bonita_variable(
            case_id, "plazos_fabricacion", "true", "java.lang.Boolean"
        )
        coleccion.assign_task(taskId)
        # Se finaliza la tarea
        coleccion.updateUserTask(taskId, "completed")

        time.sleep(5)
        taskId = coleccion.getUserTaskByName(
            "Reservar espacio de fabricación",
            case_id,
        )
        coleccion.assign_task(taskId)
        token = login_api_espacios()
        space_id = int(request.form.get("espacio"))
        reservar_api_espacios(token, space_id, id_coleccion)
        # Se finaliza la tarea
        coleccion.updateUserTask(taskId, "completed")
        flash("Espacio de fabricación reservado!", "success")
        return redirect(url_for("home"))
    flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def login_api_espacios():
    requestSession = requests.Session()
    URL = "http://127.0.0.1:7000/login"
    body = {"username": current_user.username, "password": current_user.password}
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    print(response)
    token = response.json()["token"]
    return token


@login_required
def listado_api_espacios(token, days, end_date):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:7000/espacios"
    body = {"days": days, "end_date": end_date}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    listado = response.json()
    return listado


@login_required
def reservar_api_espacios(token, space_id, id_coleccion):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:7000/reservar_espacio"
    body = {
        "space_id": space_id,
        "user_id": int(coleccion.get_user_id()),
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
def seleccionar_espacio(id_coleccion):
    """Template para seleccionar espacio espacio"""
    # cambiar a operaciones
    if session["current_rol"] == "Operaciones":
        token = login_api_espacios()
        days = int(request.form.get("dias"))
        end_date = str((Coleccion.get_by_id(id_coleccion).fecha_entrega).date())
        espacios = listado_api_espacios(token, days, end_date)
        case_id = Coleccion.get_by_id(id_coleccion).case_id
        if espacios:
            return render_template(
                "coleccion/seleccion_espacio.html",
                espacios=espacios,
                id_coleccion=id_coleccion,
            )
        else:
            coleccion.set_bonita_variable(
                case_id, "plazos_fabricacion", "false", "java.lang.Boolean"
            )
            flash("No hay espacios disponibles")
            return redirect(url_for("home"))
    flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))
