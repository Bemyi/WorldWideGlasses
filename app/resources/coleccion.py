from datetime import timedelta
import time
from flask import redirect, render_template, request, url_for, flash, session, jsonify
from flask_login import login_required
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.form.coleccion.reprogramar_coleccion import FormReprogramarColeccion
from app.form.tarea.alta_tarea import FormAltaTarea
from app.models.coleccion import Coleccion
from app.models.tarea import Tarea
from app.helpers.bonita_api import (
    init_process,
    assign_task,
    updateUserTask,
    set_bonita_variable,
    getUserTaskByName,
)

from app.models.modelo import Modelo

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
            time.sleep(6)
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
                [1, 2, 3],
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
                usuarios,
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
def reprogramar(id_coleccion):
    if session["current_rol"] == "Creativa":
        form = FormReprogramarColeccion()
        coleccion = Coleccion.get_by_id(id_coleccion)
        form.fecha_lanzamiento.data = coleccion.fecha_lanzamiento
        return render_template(
            "coleccion/reprogramar.html", coleccion=coleccion, form=form
        )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def modificar_fecha(id_coleccion):
    if session["current_rol"] == "Creativa":
        form = FormReprogramarColeccion()
        coleccion = Coleccion.get_by_id(id_coleccion)
        if form.validate_on_submit():
            time.sleep(5)
            taskId = getUserTaskByName(
                "Consulta de materiales a la API",
                Coleccion.get_by_id(id_coleccion).case_id,
            )
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            taskId = getUserTaskByName(
                "Planificación de distribución",
                Coleccion.get_by_id(id_coleccion).case_id,
            )
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            time.sleep(5)
            nueva_fecha = form.fecha_lanzamiento.data
            coleccion.modificar_lanzamiento(nueva_fecha)
            taskId = getUserTaskByName(
                "Seleccionar fecha de lanzamiento", coleccion.case_id
            )
            assign_task(taskId)
            # Se finaliza la tarea
            updateUserTask(taskId, "completed")
            # calcular_fecha_entrega(coleccion)
            time.sleep(5)
            coleccion.modificar_entrega(coleccion.fecha_lanzamiento - timedelta(30))
            return redirect(url_for("home"))
        else:
            return render_template(
                "coleccion/reprogramar.html", coleccion=coleccion, form=form
            )
    else:
        flash("danger_msg", "No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def planificar_fabricacion(id_coleccion):
    if session["current_rol"] == "Operaciones":
        form = FormAltaTarea()
        coleccion = Coleccion.get_by_id(id_coleccion)
        tareas = Tarea.get_by_coleccion_id(id_coleccion)
        return render_template(
            "coleccion/planificar_fabricacion.html",
            coleccion=coleccion,
            tareas=tareas,
            form=form,
        )
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))


@login_required
def elaborar_plan(id_coleccion):
    if session["current_rol"] == "Operaciones":
        print("hola")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    return redirect(url_for("home"))
