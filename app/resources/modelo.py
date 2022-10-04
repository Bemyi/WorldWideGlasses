from flask import redirect, render_template, url_for, flash
from flask_login import login_required
from app.form.modelo.alta_modelo import FormAltaModelo
from app.models.modelo import Modelo
from app.models.tipo import Tipo


@login_required
def crear():
    """Creación de un nuevo modelo"""
    form = FormAltaModelo()
    if form.validate_on_submit():
        nombre = form.nombre.data
        descripcion = form.descripcion.data
        tipo = form.tipo.data
        Modelo.crear(nombre, descripcion, tipo)
        flash("¡El modelo fue creado con exito!")
        return redirect(url_for("home"))
    tipos = Tipo.tipos()
    return render_template("modelo/nuevo.html", form=form, tipos=tipos)


@login_required
def nuevo():
    """Template Nuevo modelo"""
    form = FormAltaModelo()
    tipos = Tipo.tipos()
    return render_template("modelo/nuevo.html", form=form, tipos=tipos)
