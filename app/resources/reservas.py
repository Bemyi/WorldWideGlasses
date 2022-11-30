import time
from flask import redirect, render_template, url_for, flash, session, request
from flask_login import login_required, current_user
import requests
import json
from app.models.coleccion import Coleccion
from app.resources import coleccion
from app.models.material import Material
from datetime import datetime

# MATERIALES
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
        token = login_api_materiales()
        listado = listado_api_materiales(token, materiales)
        # filtramos materiales obtenidos
        mats_obtenidos = [material["name"] for material in listado]
        # filtramos stocks para utilizarlos mas adelante
        stocks = [material["stock"] for material in listado]
        if not (set(materiales) == set(mats_obtenidos)):
            materiales_faltan = [i for i in materiales if i not in mats_obtenidos]
            flash(
                "Faltan los siguientes materiales: " + str(materiales_faltan), "error"
            )
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
def login_api_materiales():
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
def listado_api_materiales(token, materiales):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:8000/materiales"
    body = {"names": materiales}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    data = json.dumps(body)
    response = requestSession.put(URL, data=data, headers=headers)
    listado = response.json()
    return listado


@login_required
def reservar_api_materiales(token, id_coleccion):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:8000/reservar_materiales"
    body = {
        "materials": eval(Coleccion.get_by_id(id_coleccion).materiales), #convierto el str a dict
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
def guardar_materiales(id_coleccion):
    if session["current_rol"] == "Operaciones":
        """Template Reservar materiales"""
        token = login_api_materiales()
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
        print(json.dumps(listado))
        Coleccion.get_by_id(id_coleccion).save_materials(str(json.dumps(listado)))
        coleccion.set_bonita_variable(
            Coleccion.get_by_id(id_coleccion).case_id,
            "materiales_fecha",
            "true",
            "java.lang.Boolean",
        )
        time.sleep(5)
        taskId = coleccion.getUserTaskByName(
            "Consulta de materiales a la API", Coleccion.get_by_id(id_coleccion).case_id
        )
        coleccion.assign_task(taskId)
        # Se finaliza la tarea
        coleccion.updateUserTask(taskId, "completed")
        time.sleep(5)
        flash("Materiales guardados!", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))

@login_required
def recibir_materiales(id_coleccion):
    if session["current_rol"] == "Operaciones":
        # Seteo la variable de bonita materiales_disponibles
        coleccion.set_bonita_variable(
            Coleccion.get_by_id(id_coleccion).case_id, "materiales_disponibles", "true", "java.lang.Boolean"
        )
        flash("Materiales recibidos!", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    # doy tiempo a que avance el proceso
    time.sleep(5)
    return redirect(url_for("home"))

# ESPACIOS
@login_required
def reservar_espacio(id_coleccion):
    """Se reserva un espacio"""
    if session["current_rol"] == "Operaciones":
        case_id = Coleccion.get_by_id(id_coleccion).case_id
        time.sleep(5)
        taskId = coleccion.getUserTaskByName(
            "Consultar espacio de fabricación",
            case_id,
        )
        # Seteo la variable de bonita plazos_fabricacion
        coleccion.set_bonita_variable(
            case_id, "plazos_fabricacion", "true", "java.lang.Boolean"
        )
        coleccion.assign_task(taskId)
        # Se finaliza la tarea
        coleccion.updateUserTask(taskId, "completed")

        # Reservo los materiales guardados (si es que no los tengo, eso lo chequea bonita automaticamente con la variable "materiales_disponibles")
        time.sleep(5)
        taskId = coleccion.getUserTaskByName(
            "Reservar materiales",
            case_id,
        )
        coleccion.assign_task(taskId)
        token = login_api_materiales()
        reservar_api_materiales(token, id_coleccion)
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
        
        #Borro los materiales guardados de la colección
        Coleccion.get_by_id(id_coleccion).delete_materials()
        
        flash("Materiales y espacio de fabricación reservados!", "success")
    else:
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
def listado_api_espacios(token, end_date):
    requestSession = requests.Session()
    URL = "http://127.0.0.1:7000/espacios"
    body = {"end_date": end_date}
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
        end_date = str((Coleccion.get_by_id(id_coleccion).fecha_entrega).date())
        espacios = listado_api_espacios(token, end_date)
        case_id = Coleccion.get_by_id(id_coleccion).case_id
        if espacios:
            return render_template(
                "coleccion/seleccion_espacio.html",
                espacios=espacios,
                id_coleccion=id_coleccion,
                fecha_entrega=Coleccion.get_by_id(id_coleccion).fecha_entrega,
                fecha_actual=datetime.now()
            )
        else:
            coleccion.set_bonita_variable(
                case_id, "plazos_fabricacion", "false", "java.lang.Boolean"
            )
            flash("No hay espacios disponibles", "error")
            return redirect(url_for("home"))
    flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))
