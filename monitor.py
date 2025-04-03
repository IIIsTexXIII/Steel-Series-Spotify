# Crear un archivo de texto en la siguiente ruta "C:\Users\TU_USUARIO\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
# El archivo debe tener el siguiente contenido:
#
# @echo off
# python "C:\Ruta\A\Tu\monitor.py"
#
#
# IMPORTANTE GUARDARLO CON LA EXTENSION .bat


import os
import time
import psutil
import subprocess

# Ruta a tu script principal
SCRIPT_PATH = (
    'python "C:/Users/andre/Desktop/sonar spotify/Steel-Series-Spotify/main.py"'
)


def is_spotify_running():
    """Verifica si Spotify está en ejecución."""
    for process in psutil.process_iter(["name"]):
        if process.info["name"] and "Spotify.exe" in process.info["name"]:
            return True
    return False


def main():
    process = None
    while True:
        if is_spotify_running():
            if process is None or process.poll() is not None:
                print("Spotify detectado, ejecutando script...")
                process = subprocess.Popen(
                    SCRIPT_PATH, shell=True
                )  # Ejecuta el script principal
        else:
            if process and process.poll() is None:
                print("Spotify cerrado, deteniendo script...")
                process.terminate()  # Mata el proceso del script
                process = None

        time.sleep(2)  # Verifica cada 2 segundos


if __name__ == "__main__":
    main()
