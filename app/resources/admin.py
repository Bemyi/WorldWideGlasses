import json
from flask import redirect, render_template, session, url_for, flash
from flask_login import login_required
import requests
from app.form.admin.alta_usuario import FormAltaUsuario
from app.models.usuario import Usuario

@login_required
def nuevo_usuario():
    """Template nuevo usuario"""
    form = FormAltaUsuario() 
    return render_template("admin/create_user.html", form=form)

@login_required
def crear_usuario():
    """Creación de un nuevo usuario"""
    form = FormAltaUsuario()
    if form.validate_on_submit():
        print("Todo ok el form :D")
        email = form.email.data
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data

        user = Usuario.query.filter_by(email=email).first()  
        if not user:
            print("No existe el user :D")
            # agregar el usuario a Bonita
            create_bonita_user(username, first_name, last_name, password)
            # crear el usuario en la BD
            #Usuario.crear(email, username, first_name, last_name, password)
        flash("¡El usuario fue creado con exito!")
        return redirect(url_for("home"))
    print("Por alguna razón no se creó :(")
    return render_template("admin/create_user.html", form=form)

@login_required
def create_bonita_user(username, first_name, last_name, password): #no usa mail
    requestSession = requests.Session()
    URL="http://localhost:8080/bonita/API/identity/user/"
    headers={
        "Content-type":"application/json",
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"]
    }
    data={"userName":username,"password":password,"firstname":first_name,"lastname":last_name, "enabled": "true"}
    data = json.dumps(data)
    response, content = requestSession.post(URL, headers=headers, body=data)
    if response.status_code==200:
        data = json.loads(content)
        print("ID nuevo user: "+data['id'])