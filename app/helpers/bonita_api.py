from flask_login import current_user, login_required
import requests
import json
from flask import session


@login_required
def getActiveCases():
    """Se recupera los cases activos"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/userTask"
    headers = getBonitaHeaders()
    params = {"d": "actorId", "f": "state=ready"}
    response = requestSession.get(URL, headers=headers, params=params)
    print("Response:")
    print(response)
    return response.json()


def getClosedCases():
    """Se recupera los cases activos"""
    requestSession = requests.Session()
    URL = "http://localhost:8080/bonita/API/bpm/archivedCase"
    headers = getBonitaHeaders()
    params = {"name": "Creación de colección"}
    response = requestSession.get(URL, headers=headers, params=params)
    print("Response:")
    print(response)
    return response.json()


@login_required
def getBonitaHeaders():
    headers = {
        "Cookie": session["JSESSION"],
        "X-Bonita-API-Token": session["bonita_token"],
        "Content-Type": "application/json",
    }
    return headers
