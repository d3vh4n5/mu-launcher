import hashlib
from tkinter import StringVar, Label
from customtkinter import CTkComboBox, CTkProgressBar, CTkButton, CTkLabel
from const.colors import *
from const.config import API_URL, components_width
from const.texts import TEXTS
from utils.state import AppState
from services.api_service import ServerService
import threading
import requests
import os

def load_frame_update(frame1, state: AppState, btn_play):
    # 1. Definimos la etiqueta y la variable
    label_status = CTkLabel(
        frame1,
        # bg="black",
        # fg="white",
        text="Status"
    )
    label_status.pack()

    # Barra de progreso (inicialmente oculta o en 0)
    progress_bar = CTkProgressBar(
        frame1, 
        width=components_width, 
        progress_color=primary_color,
        mode="determinate" # O "indeterminate" si no sabemos el tamaño
    )
    progress_bar.set(0) # Empezar en 0
    progress_bar.pack(pady=10)
    #progress_bar.pack_forget() # La ocultamos hasta que se necesite

    def calcular_sha256(path):
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for bloque in iter(lambda: f.read(8192), b""):
                sha256.update(bloque)
        return sha256.hexdigest()
    
    def iniciar_update():
        # Corremos el update en un hilo separado
        thread = threading.Thread(target=proceso_verificacion)
        thread.daemon = True
        thread.start()

    def proceso_verificacion():
        btn_play.configure(state="disabled") # Evitar que juegue durante la actualización
        btn_update.configure(state="disabled", text="Verificando...") # Evitar múltiples clicks
        CLIENT_URL = API_URL + "/downloads/Mu99bClassic/Client/" # Donde subiste los archivos
        MANIFEST_URL = API_URL + "/downloads/Mu99bClassic/manifest.json" # Donde subiste los archivos
        
        # 1. Bajamos el manifest.json del servidor
        try:
            r = requests.get(MANIFEST_URL)
            remote_manifest = r.json()
        except:
            label_status.configure(text="Error de conexión con el servidor")
            return

        archivos = remote_manifest["files"]
        total = remote_manifest["file_count"]

        for i, item in enumerate(archivos):
            path_local = item["path"]
            hash_remoto = item["sha256"]
            
            # Actualizar UI
            label_status.configure(text=f"Verificando: {path_local}")
            progress_bar.set(i / total)

            # 2. Check de existencia y Hash
            descargar = False
            if not os.path.exists(path_local):
                descargar = True
            else:
                if calcular_sha256(path_local) != hash_remoto:
                    descargar = True

            # 3. Descarga real si hace falta
            if descargar:
                label_status.configure(text=f"Descargando: {path_local}")
                
                # 1. Obtener el nombre del directorio
                directorio = os.path.dirname(path_local)
                
                # 2. Solo crear si NO es la raíz (si directorio no está vacío)
                if directorio:
                    os.makedirs(directorio, exist_ok=True)
                
                # 3. Proceder con la descarga
                r_file = requests.get(CLIENT_URL + path_local)
                with open(path_local, "wb") as f:
                    f.write(r_file.content)

        label_status.configure(text="¡Cliente actualizado! Ya podés jugar.")
        btn_play.configure(state="normal")
        btn_update.configure(state="normal", text="Verificar y Actualizar Cliente")

    # Botón para iniciar la verificación/actualización
    btn_update = CTkButton(
        frame1,
        text="Verificar y Actualizar Cliente",
        width=components_width,
        fg_color=primary_color,
        command=iniciar_update
    )
    btn_update.pack(pady=10)