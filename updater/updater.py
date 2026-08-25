import base64
import os
import sys
import time
import argparse
import subprocess
import threading
from pathlib import Path

# Asegurar que el directorio raíz esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import customtkinter as ctk
from assets.icono_data import ICONO_BASE64
from const.colors import bg_color, primary_color
import psutil

class UpdaterGUI(ctk.CTk):
    def __init__(self, new_exe_path, target_exe_path, parent_pid=None):
        super().__init__()

        self.new_exe_path = Path(new_exe_path)
        self.target_exe_path = Path(target_exe_path)
        self.parent_pid = parent_pid

        # Configuración de ventana
        ctk.set_appearance_mode("dark")
        self.title("Actualizador de Mu Launcher")
        self.geometry("340x190")
        self.resizable(False, False)
        self.configure(fg_color=bg_color)
        self.attributes("-alpha", 0.9)
        self._set_icon()

        # Centrar ventana
        try:
            self.eval('tk::PlaceWindow . center')
        except Exception:
            pass

        # Titulo
        self.lbl_title = ctk.CTkLabel(
            self,
            text="Actualizando Launcher",
            font=("Arial", 15, "bold"),
            text_color="white",
        )
        self.lbl_title.pack(pady=(22, 4))

        # Subtitulo de estado
        self.lbl_status = ctk.CTkLabel(
            self,
            text="Iniciando proceso de actualización...",
            font=("Arial", 10),
            text_color="#ADADAD",
        )
        self.lbl_status.pack(pady=(0, 8))

        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=280,
            progress_color=primary_color,
            mode="determinate"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        # Hilo de ejecución
        self.thread = threading.Thread(target=self.run_update_process, daemon=True)
        self.after(500, self.thread.start)

    def _set_icon(self):
        try:
            icon_path = BASE_DIR / "data" / "temp" / "updater_icon.ico"
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            icon_path.write_bytes(base64.b64decode(ICONO_BASE64))
            self.iconbitmap(str(icon_path))
        except Exception as error:
            print(f"No se pudo cargar el icono del updater: {error}")

    def set_status(self, text, progress=None):
        def _update():
            self.lbl_status.configure(text=text)
            if progress is not None:
                self.progress_bar.set(progress)
        self.after(0, _update)

    def run_update_process(self):
        try:
            # 1. Esperar cierre del proceso principal si se pasó PID
            if self.parent_pid:
                self.set_status("Esperando cierre del launcher...", 0.2)
                try:
                    proc = psutil.Process(int(self.parent_pid))
                    proc.wait(timeout=8)
                except (psutil.NoSuchProcess, Exception):
                    pass
            time.sleep(0.8)

            # 2. Forzar liberación si queda algún proceso remanente
            self.set_status("Verificando procesos del launcher...", 0.4)
            from updater.process import force_close_launcher
            force_close_launcher(self.target_exe_path.name)
            time.sleep(0.5)

            # 3. Reemplazar ejecutable
            self.set_status("Aplicando la nueva versión...", 0.7)
            from updater.files import update_executable

            if not self.new_exe_path.exists():
                raise FileNotFoundError(f"No se encontró el ejecutable nuevo en:\n{self.new_exe_path}")

            success = update_executable(self.target_exe_path, self.new_exe_path)
            if not success:
                raise RuntimeError("No se pudo reemplazar el ejecutable del launcher.")

            # 4. Finalizado exitoso
            self.set_status("¡Actualización completada! Reabriendo...", 1.0)
            time.sleep(1.2)

            # 5. Iniciar la nueva versión
            if self.target_exe_path.exists():
                subprocess.Popen(str(self.target_exe_path), cwd=str(self.target_exe_path.parent))

        except Exception as e:
            self.set_status(f"Error: {e}", 0)
            time.sleep(3.5)
        finally:
            self.after(0, self.destroy)


def start_updater_gui(new_exe, target_exe, pid=None):
    app = UpdaterGUI(new_exe_path=new_exe, target_exe_path=target_exe, parent_pid=pid)
    app.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Actualizador del Launcher de Mu")
    parser.add_argument("--new-exe", type=str, help="Ruta al nuevo ejecutable descargado")
    parser.add_argument("--target-exe", type=str, help="Ruta al ejecutable launcher.exe a reemplazar")
    parser.add_argument("--pid", type=int, help="PID del proceso launcher a esperar")

    args = parser.parse_args()

    default_new = BASE_DIR / "data" / "launcher" / "launcher-new.exe"
    default_target = BASE_DIR / "launcher.exe"

    new_exe_arg = args.new_exe or str(default_new)
    target_exe_arg = args.target_exe or str(default_target)

    start_updater_gui(new_exe_arg, target_exe_arg, args.pid)