import hashlib
from tkinter import StringVar, Label
from customtkinter import CTkComboBox, CTkProgressBar, CTkButton, CTkLabel
from const.colors import *
from const.config import API_URL, API_KEY, components_width
from const.texts import TEXTS
from utils.state import AppState
from utils.logger import logger
import threading
import requests
import os
import urllib.parse

def load_frame_update(frame1, state: AppState, btn_play):
    def get_txt(key, default=""):
        lang = state.lang.get()
        return TEXTS.get(lang, TEXTS.get("Spn", {})).get(key, default)

    # 1. Definimos la etiqueta y la variable
    label_status = CTkLabel(
        frame1,
        text=get_txt("status_ready", "Estado: Listo")
    )
    label_status.pack()

    # Barra de progreso
    progress_bar = CTkProgressBar(
        frame1, 
        width=components_width, 
        progress_color=primary_color,
        mode="determinate"
    )
    progress_bar.set(0)
    progress_bar.pack(pady=10)

    def update_ui_status(text, progress=None):
        def _update():
            label_status.configure(text=text)
            if progress is not None:
                progress_bar.set(progress)
        frame1.after(0, _update)

    def calcular_sha256(path):
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for bloque in iter(lambda: f.read(8192), b""):
                sha256.update(bloque)
        return sha256.hexdigest()
    
    def iniciar_update():
        thread = threading.Thread(target=proceso_verificacion)
        thread.daemon = True
        thread.start()

    def proceso_verificacion():
        frame1.after(0, lambda: btn_play.configure(state="disabled"))
        txt_verifying = get_txt("verifying", "Verificando...")
        frame1.after(0, lambda: btn_update.configure(state="disabled", text=txt_verifying))

        headers = {
            "x-api-key": API_KEY
        }

        CLIENT_URL = API_URL + "/downloads/Mu99bClassic/Client/"
        MANIFEST_URL = API_URL + "/downloads/Mu99bClassic/manifest.json"
        
        try:
            update_ui_status(get_txt("connecting_server", "Conectando con el servidor..."), 0)
            r = requests.get(MANIFEST_URL, headers=headers, timeout=15)
            r.raise_for_status()
            remote_manifest = r.json()

            archivos = remote_manifest.get("files", [])
            total = remote_manifest.get("file_count", len(archivos))

            if total == 0:
                update_ui_status(get_txt("client_updated", "¡Cliente actualizado! Ya podés jugar."), 1.0)
                return

            txt_verifying_label = get_txt("verifying", "Verificando")
            txt_downloading_label = get_txt("downloading", "Descargando")

            for i, item in enumerate(archivos):
                path_local = item["path"]
                hash_remoto = item["sha256"]
                
                path_local_norm = os.path.normpath(path_local)
                progress_val = i / total
                update_ui_status(f"{txt_verifying_label} ({i+1}/{total}): {path_local_norm}", progress_val)

                # Check de existencia y Hash
                descargar = False
                if not os.path.exists(path_local_norm):
                    descargar = True
                else:
                    if calcular_sha256(path_local_norm) != hash_remoto:
                        descargar = True

                # Descarga real si hace falta
                if descargar:
                    update_ui_status(f"{txt_downloading_label} ({i+1}/{total}): {path_local_norm}", progress_val)
                    
                    directorio = os.path.dirname(path_local_norm)
                    if directorio:
                        os.makedirs(directorio, exist_ok=True)
                    
                    url_relativa = urllib.parse.quote(path_local.replace("\\", "/"))
                    file_url = CLIENT_URL + url_relativa
                    
                    r_file = requests.get(file_url, headers=headers, timeout=30)
                    r_file.raise_for_status()
                    
                    with open(path_local_norm, "wb") as f:
                        f.write(r_file.content)

            update_ui_status(get_txt("client_updated", "¡Cliente actualizado! Ya podés jugar."), 1.0)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red durante la actualización: {e}", exc_info=True)
            update_ui_status(get_txt("connection_error", "Error de conexión con el servidor"), 0)
        except Exception as e:
            logger.error(f"Error durante la actualización: {e}", exc_info=True)
            txt_err = get_txt("error", "Error")
            update_ui_status(f"{txt_err}: {e}", 0)
        finally:
            txt_btn_normal = get_txt("verify_update_btn", "Verificar y Actualizar Cliente ⬇️⏬")
            txt_play_normal = TEXTS.get(state.lang.get(), TEXTS.get("Spn", {})).get("play", "JUGAR")
            frame1.after(0, lambda: btn_play.configure(state="normal", text=f"{txt_play_normal}     "))
            frame1.after(0, lambda: btn_update.configure(state="normal", text=txt_btn_normal))

    # Botón para iniciar la verificación/actualización
    btn_update = CTkButton(
        frame1,
        text=get_txt("verify_update_btn", "Verificar y Actualizar Cliente ⬇️⏬"),
        width=components_width,
        fg_color=primary_color,
        command=iniciar_update
    )
    btn_update.pack(pady=10)

    def update_language_texts(*args):
        btn_update.configure(text=get_txt("verify_update_btn", "Verificar y Actualizar Cliente ⬇️⏬"))
        label_status.configure(text=get_txt("status_ready", "Estado: Listo"))

    state.lang.trace_add("write", update_language_texts)

