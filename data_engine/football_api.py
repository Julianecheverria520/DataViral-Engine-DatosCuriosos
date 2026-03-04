import os
import requests
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")

if not API_KEY:
    raise ValueError("No se encontró FOOTBALL_API_KEY en .env")

headers = {
    "Authorization": f"Token {API_KEY}"
}

url = "https://sports.bzzoiro.com/api/teams/"

try:
    response = requests.get(url, headers=headers)

    print("Status Code:", response.status_code)

    if response.status_code == 200:
        print(response.json())
    else:
        print("Error:", response.text)

except Exception as e:
    print("Error en la solicitud:", e)