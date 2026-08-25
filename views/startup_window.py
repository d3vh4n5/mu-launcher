import base64
import sys
import threading
from pathlib import Path
from tkinter import Label

import customtkinter as ctk

from assets.icono_data import ICONO_BASE64
from const.colors import bg_color, primary_color
from services.launcher_update_service import check_and_update_launcher
from updater import trigger_launcher_update
from utils.logger import logger
from views.app import App


class StartupWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Mu Campana")
        self.window.geometry("320x150")
        self.window.resizable(False, False)
        self.window.configure(fg_color=bg_color)
        self.window.attributes("-alpha", 0.9)
        self._set_icon()
        self.window.eval("tk::PlaceWindow . center")

        self.title_label = ctk.CTkLabel(
            self.window,
            text="Cargando...",
            font=("Arial", 15, "bold"),
            text_color="white",
        )
        self.title_label.pack(pady=(22, 4))

        self.status_label = ctk.CTkLabel(
            self.window,
            text="Verificando actualizaciones",
            font=("Arial", 10),
            text_color="#ADADAD",
        )
        self.status_label.pack(pady=(0, 8))

        self.progress_bar = ctk.CTkProgressBar(
            self.window,
            width=260,
            progress_color=primary_color,
            mode="indeterminate",
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)
        self.progress_bar.start()

    def _set_icon(self):
        try:
            icon_path = Path("temp_icon.ico")
            icon_path.write_bytes(base64.b64decode(ICONO_BASE64))
            self.window.iconbitmap(str(icon_path))
            icon_path.unlink(missing_ok=True)
        except Exception as error:
            logger.debug(f"No se pudo cargar el icono de inicio: {error}")

    def update_progress(self, message, progress=None):
        def update_ui():
            self.status_label.configure(text=message)
            if progress is not None:
                self.progress_bar.stop()
                self.progress_bar.configure(mode="determinate")
                self.progress_bar.set(progress)

        self.window.after(0, update_ui)

    def start(self):
        threading.Thread(target=self._check_updates, daemon=True).start()
        self.window.mainloop()

    def _check_updates(self):
        if not getattr(sys, "frozen", False):
            print("[launcher] Iniciando chequeo de actualización...")

        launcher_info = check_and_update_launcher(self.update_progress)
        self.window.after(0, self._finish_startup, launcher_info)

    def _finish_startup(self, launcher_info):
        new_launcher_path = launcher_info.get("_new_launcher_path") if launcher_info else None
        if new_launcher_path:
            self.update_progress("Iniciando actualizador...", 1.0)
            self.window.update_idletasks()
            if not getattr(sys, "frozen", False):
                print("[launcher] Ejecutando updater y cerrando launcher actual.")
            self.window.destroy()
            trigger_launcher_update(
                Path(new_launcher_path),
                Path(launcher_info["_current_exe"]),
            )
            return

        self.window.destroy()
        if not getattr(sys, "frozen", False):
            print("[launcher] Chequeo finalizado. Abriendo interfaz principal.")
        App(launcher_info.get("registerUrl") if launcher_info else None)


def start_application():
    StartupWindow().start()
