from flask_login import current_user, login_required
import requests
import json
from flask import session


@login_required
def getActiveCases():
    """Se recupera los cases activos"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/case"
    headers = getBonitaHeaders()
    params = {"state": "started"}
    response = requestSession.get(URL, headers=headers, params=params)
    print("Response del getActiveCases:")
    print(response)
    print(response.json())
    return response.json()


def getClosedCases():
    """Se recupera los cases activos"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/archivedCase"
    headers = getBonitaHeaders()
    params = {"name": "Creación de colección"}
    response = requestSession.get(URL, headers=headers, params=params)
    print("Response del getClosedCases:")
    print(response)
    print(response.json())
    return response.json()


@login_required
def init_process():
    # se le pega a la API y se recupera el id del proceso
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/process?s=Creación de colección"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response del get id del proceso:")
    print(response)
    processId = response.json()[0]["id"]
    print("Process ID: " + response.json()[0]["id"])

    # se instancia el proceso con su id, creando una tarea
    URL = "http://localhost:8080/bonita/API/bpm/process/" + processId + "/instantiation"
    headers = getBonitaHeaders()
    response = requestSession.post(URL, headers=headers)

    print("Response al instanciar proceso:")
    print(response)
    print(response.json())
    case_id = response.json()["caseId"]
    print("Case ID:")
    print(case_id)
    return case_id


@login_required
def get_user_id():
    """Se recupera el id del usuario logeado"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/system/session/unusedId"
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response del get user id:")
    print(response)
    print(response.json()["user_id"])
    user_id = response.json()["user_id"]
    return user_id


@login_required
def assign_task(taskId):
    """Se le asigna una tarea al usuario logeado"""
    requestSession = requests.Session()
    user_id = get_user_id()
    URL = "http://localhost:8080/bonita/API/bpm/humanTask/" + taskId
    headers = getBonitaHeaders()
    body = {"assigned_id": user_id}
    # Lo convierto a json porque sino tira 500
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)
    print(response)


@login_required
def updateUserTask(taskId, state):
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/humanTask/" + taskId
    headers = getBonitaHeaders()
    body = {"state": state}
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)
    print("Print del update user task:")
    print(response)


@login_required
def set_bonita_variable(case_id, variable_name, variable_value, type):
    """setea un valor a la variable que es pasada por parametro"""
    requestSession = requests.Session()
    URL = (
        "http://localhost:8080/bonita/API/bpm/caseVariable/"
        + str(case_id)
        + "/"
        + variable_name
    )
    body = {"value": variable_value, "type": type}
    headers = getBonitaHeaders()
    data = json.dumps(body)
    response = requestSession.put(URL, headers=headers, data=data)
    print("Response de setear variable bonita:")
    print(response)
    response = requestSession.get(URL, headers=headers)
    print("Response al hacer get de variable bonita:")
    print(response)
    print("Valor de la variable"+variable_name+":")
    print(response.json()["value"])

@login_required
def get_bonita_variable(case_id, variable_name):
    """setea un valor a la variable que es pasada por parametro"""
    requestSession = requests.Session()
    URL = (
        "http://localhost:8080/bonita/API/bpm/caseVariable/"
        + str(case_id)
        + "/"
        + variable_name
    )
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response de get variable bonita para la variable "+variable_name+":")
    print(response)
    print("Valor de la variable "+variable_name+":")
    print(response.json()["value"])
    return response.json()["value"]


@login_required
def getUserTaskByName(taskName, caseId):
    """Obtengo la tarea por su case y name para tener su id"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/humanTask?f=caseId="+str(caseId)+"&f=name="+taskName
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response del get user task para el case "+str(caseId)+":")
    print(URL)
    print(response)
    print(response.json())
    print(response.json()[0]["id"])
    taskId = response.json()[0]["id"]
    return taskId


def get_ready_tasks(case_id):
    requestSession = requests.Session()
    URL = (
        "http://localhost:8080/bonita/API/bpm/humanTask/"
    )
    headers = getBonitaHeaders()
    params = {"f": "caseId="+str(case_id)}
    response = requestSession.get(URL, headers=headers, params=params)
    print("Response del get tareas ready para el case "+str(case_id)+":")
    tareas = []
    print(response.status_code)
    if response.status_code == 200:
        tareas = [task["name"] for task in response.json()]
    print(tareas)
    return tareas


def get_completed_tasks_by_name(case_id, name):
    requestSession = requests.Session()
    URL = (
        "http://localhost:8080/bonita/API/bpm/archivedHumanTask?f=caseId="+str(case_id)+"&f=name="+name
    )
    headers = getBonitaHeaders()
    response = requestSession.get(URL, headers=headers)
    print("Response del get tareas completed para el case "+str(case_id)+":")
    tareas = []
    print(response.status_code)
    if response.status_code == 200:
        tareas = [task["name"] for task in response.json()]
    print(tareas)
    return tareas


def deleteCase(case_id):
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/case/" + str(case_id)
    headers = getBonitaHeaders()
    response = requestSession.delete(URL, headers=headers)
    print(response.status_code)


@login_required
def getBonitaHeaders():
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
        "Content-Type": "application/json",
    }
    return headers
