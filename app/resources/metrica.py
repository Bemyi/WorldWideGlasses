from flask import redirect, render_template, url_for, flash, session, request
from flask_login import login_required
from app.helpers.bonita_api import getActiveCases, getClosedCases
from app.models.coleccion import Coleccion


@login_required
def index():
    """Lista de metricas"""
    # que rol debería ser?
    # if session["current_rol"] == "Creativa":
    casosActivos = len(getActiveCases())
    casosCerrados = len(getClosedCases())
    cantidadDeColeccionesCreadas = len(Coleccion.get_all_colections())
    modelosMasUsados = Coleccion.get_most_used_model()
    return render_template(
        "metrica/index.html",
        casosActivos=casosActivos,
        casosCerrados=casosCerrados,
        cantidadDeColeccionesCreadas=cantidadDeColeccionesCreadas,
    )
