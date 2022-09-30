from flask import redirect, render_template, url_for, flash
from flask_login import login_required
from app.form.coleccion.alta_coleccion import FormAltaColeccion
from app.models.coleccion import Coleccion


@login_required
def crear():
    """Creación de una nueva coleccion"""
    form = FormAltaColeccion()
    if form.validate_on_submit():
        nombre = form.nombre.data
        plazo_fabricacion = form.plazo_fabricacion.data
        fecha_lanzamiento = form.fecha_lanzamiento.data
        Coleccion.crear(nombre, plazo_fabricacion, fecha_lanzamiento)
        flash("¡La colección fue creada con exito!")
        return redirect(url_for("home"))
    return render_template("coleccion/nuevo.html", form=form)


@login_required
def nuevo():
    """Template Nueva coleccion"""
    form = FormAltaColeccion()
    return render_template("coleccion/nuevo.html", form=form)
