import time
from flask import redirect, render_template, url_for, flash, session, request
from flask_login import login_required, current_user
import requests
import json
from app.models.tarea import Tarea
from app.models.coleccion import Coleccion
from app.form.tarea.alta_tarea import FormAltaTarea
from datetime import datetime
from app.helpers.bonita_api import(
    set_bonita_variable
)


@login_required
def crear_tarea(id_coleccion):
    coleccion = Coleccion.get_by_id(id_coleccion)
    if session["current_rol"] == "Operaciones":
        form = FormAltaTarea()
        form.fin_fabricacion = coleccion.fin_fabricacion
        form.id_coleccion = id_coleccion
        if  form.validate_on_submit():
            nombre = form.nombre.data
            descripcion = form.descripcion.data
            fecha_limite = form.fecha_limite.data
            Tarea.crear(nombre, descripcion, fecha_limite, id_coleccion)
            flash("Tarea creada", "success")
        else:
            flash("Hay errores en los campos de la tarea", "error")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    tareas = Tarea.get_by_coleccion_id(id_coleccion)
    return render_template(
        "coleccion/planificar_fabricacion.html", coleccion=coleccion, tareas=tareas, form=form
    )

@login_required
def eliminar_tarea(id_coleccion, id_tarea):
    if session["current_rol"] == "Operaciones":
        tarea = Tarea.get_by_id(id_tarea)
        tarea.eliminar()
        flash("Tarea eliminada", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    tareas = Tarea.get_by_coleccion_id(id_coleccion)
    form = FormAltaTarea()
    return render_template(
        "coleccion/planificar_fabricacion.html", coleccion=Coleccion.get_by_id(id_coleccion), tareas=tareas, form=form
    )

@login_required
def finalizar_tarea(id_coleccion, id_tarea):
    if session["current_rol"] == "Operaciones":
        tarea = Tarea.get_by_id(id_tarea)
        tarea.finalizar()
        if Tarea.coleccion_finalizada(id_coleccion):
            set_bonita_variable(
                    Coleccion.get_by_id(id_coleccion).case_id, "tareas_terminadas", "true", "java.lang.Boolean"
            )
            set_bonita_variable(
                    Coleccion.get_by_id(id_coleccion).case_id, "coleccion_fabricada", "true", "java.lang.Boolean"
            )
            flash("Tareas finalizadas", "success")
            return redirect(url_for("home"))
        else:
            flash("Tarea finalizada", "success")
    else:
        flash("No tienes permiso para acceder a este sitio", "error")
    tareas = Tarea.get_by_coleccion_id(id_coleccion)
    form = FormAltaTarea()
    return render_template(
        "coleccion/administrar_tareas.html", coleccion=Coleccion.get_by_id(id_coleccion), tareas=tareas, form=form
    )
