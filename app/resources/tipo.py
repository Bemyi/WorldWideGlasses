from flask import redirect, render_template, url_for, flash, session
from flask_login import login_required
from app.form.tipo.alta_tipo import FormAltaTipo
from app.models.tipo import Tipo


@login_required
def crear():
    """Creación de un nuevo tipo de anteojo"""
    form = FormAltaTipo()
    if form.validate_on_submit():
        nombre = form.nombre.data
        Tipo.crear(nombre)
        flash("¡El tipo de anteojo fue creado con exito!")
        return redirect(url_for("home"))
    return render_template("tipo/nuevo.html", form=form)


@login_required
def nuevo():
    if session["current_rol"] == "Creativa":
        """Template Nuevo tipo de anteojo"""
        form = FormAltaTipo()
        return render_template("tipo/nuevo.html", form=form)
    flash("error", "No tienes permiso para acceder a este sitio")
    return redirect(url_for("home"))
