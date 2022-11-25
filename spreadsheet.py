import gspread
from oauth2client.service_account import ServiceAccountCredentials
from app.models.coleccion import Coleccion

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)

client = gspread.authorize(creds)

sheet = client.open("Prueba").sheet1

# list_of_hashes = sheet.get_all_values()
# print(list_of_hashes)

c = Coleccion.get_by_name("Colección 2.0")
print("AAA")
print(c)

row = [c.name, c.fecha_lanzamiento, "22/02/2012"]
index = len(sheet.get_all_values()) + 1
sheet.insert_row(row, index)
