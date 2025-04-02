import requests
import time
import json
import os
import base64
from dotenv import load_dotenv


# Configuración para mostrar el nombre del artista
ARTIST = True

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de Spotify API
SPOTIFY_ACCESS_TOKEN = os.getenv("SPOTIFY_ACCESS_TOKEN")
SPOTIFY_NOW_PLAYING_URL = "https://api.spotify.com/v1/me/player/currently-playing"

# Credenciales de tu aplicación de Spotify
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
print(REFRESH_TOKEN)

# Configuración de SteelSeries Engine API
programdata = os.getenv("PROGRAMDATA")
with open(
    programdata + "\SteelSeries\SteelSeries Engine 3\coreProps.json"
) as SSEcoreProps:
    coreProps = json.load(SSEcoreProps)
STEELSERIES_URL = "http://" + coreProps["address"]
GAME_NAME = "MY_SPOTIFY_APP_ANCAVI"

headers = {"Content-Type": "application/json"}


def refresh_access_token():
    url = "https://accounts.spotify.com/api/token"

    # Codificar las credenciales en Base64
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        new_token = response.json()["access_token"]
        print("Nuevo Access Token:", new_token)
        return new_token
    else:
        print("Error al renovar token:", response.status_code, response.text)
        return None


def get_spotify_now_playing():
    access_token = refresh_access_token()  # Obtiene un nuevo token antes de la petición

    if not access_token:
        return "Error al obtener token"

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(SPOTIFY_NOW_PLAYING_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data and "item" in data:
            track = data["item"]["name"]
            artist = data["item"]["artists"][0]["name"]
            progress_ms = data["progress_ms"] // 1000  # Convertir a segundos
            duration_ms = data["item"]["duration_ms"] // 1000  # Convertir a segundos
            progress_bar = generate_progress_bar(progress_ms, duration_ms)
            if ARTIST:
                return f"{track}\n{artist}\n{progress_bar}"
            else:
                return f"{track}\n{progress_bar}"

    return "No hay reproducción activa"


def generate_progress_bar(progress, duration, length=10):
    filled = int((progress / duration) * length) if duration > 0 else 0
    bar = "█" * filled + "─" * (length - filled)

    # Convertir segundos a formato mm:ss
    def format_time(seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02}"

    return f"{format_time(progress)} {bar}"


def register_game():
    payload = {
        "game": GAME_NAME,
        "game_display_name": "Spotify",
        "developer": "Usuario",
    }
    r = requests.post(STEELSERIES_URL + "/game_metadata", json=payload, headers=headers)


def register_event():
    if ARTIST:
        lines = [
            {"has-text": True, "context-frame-key": "text"},
            {"has-text": True, "context-frame-key": "artist"},
            {"has-text": True, "context-frame-key": "progress"},
        ]
    else:
        lines = [
            {"has-text": True, "context-frame-key": "text"},
            {"has-text": True, "context-frame-key": "progress"},
        ]
    payload = {
        "game": GAME_NAME,
        "event": "NOW_PLAYING",
        "value_optional": True,
        "handlers": [
            {
                "device-type": "screened",
                "mode": "screen",
                "datas": [{"lines": lines}],
            }
        ],
    }
    response = requests.post(
        STEELSERIES_URL + "/bind_game_event", json=payload, headers=headers
    )
    print("Register Event Response:", response.status_code, response.text)


def update_display(text):

    if ARTIST:
        if "\n" in text:
            track, artist, progress = text.split("\n", 2)
        else:
            track, artist, progress = text, "", ""
        frame = {
            "text": track[:30],  # Máximo 30 caracteres
            "artist": artist[:30],  # Máximo 30 caracteres
            "progress": progress[:30],  # Máximo 30 caracteres
        }
    else:
        if "\n" in text:
            track, progress = text.split("\n", 1)
        else:
            track, progress = text, ""
        frame = {
            "text": track[:30],  # Máximo 30 caracteres
            "progress": progress[:30],  # Máximo 30 caracteres
        }
    payload = {
        "game": GAME_NAME,
        "event": "NOW_PLAYING",
        "data": {"frame": frame},
    }
    response = requests.post(
        STEELSERIES_URL + "/game_event", json=payload, headers=headers
    )
    print(f"Update Display Response: {response.status_code} - {response.text}")


def main():
    register_game()
    register_event()
    while True:
        now_playing = get_spotify_now_playing()
        update_display(now_playing)
        time.sleep(0.5)  # Actualiza cada 5 segundos


if __name__ == "__main__":
    main()
