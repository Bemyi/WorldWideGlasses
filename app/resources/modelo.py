from flask import redirect, render_template, url_for, flash, session, request
from flask_login import login_required
from app.form.modelo.alta_modelo import FormAltaModelo
from app.models.modelo import Modelo
from app.models.tipo import Tipo


@login_required
def crear():
    """Creación de un nuevo modelo"""
    if session["current_rol"] == "Creativa":
        form = FormAltaModelo()
        if form.validate_on_submit():
            nombre = form.nombre.data
            descripcion = form.descripcion.data
            tipo = request.form.get("tipo")
            Modelo.crear(nombre, descripcion, tipo)
            flash("¡El modelo fue creado con exito!")
            return redirect(url_for("home"))
        tipos = Tipo.tipos()
        return render_template("modelo/nuevo.html", form=form, tipos=tipos)
    flash("No tienes permiso para acceder a este sitio")
    return redirect(url_for("home"))


@login_required
def nuevo():
    if session["current_rol"] == "Creativa":
        """Template Nuevo modelo"""
        form = FormAltaModelo()
        tipos = Tipo.tipos()
        return render_template("modelo/nuevo.html", form=form, tipos=tipos)
    flash("No tienes permiso para acceder a este sitio")
    return redirect(url_for("home"))
