from tkinter import ttk, messagebox

import shutil
import subprocess
import winreg

from const.config import *

# =========================
# FUNCIONES
# =========================

def set_window_mode(windowed: bool):
    try:
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Webzen\MU\config"
        )

        # Modo ventana
        winreg.SetValueEx(
            key,
            "WindowMode",
            0,
            winreg.REG_DWORD,
            1 if windowed else 0
        )
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"No se pudo escribir en el registro\n{e}"
        )

def set_window_resolution(resolution: int, ):
    try:
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Webzen\MU\config"
        )

        resolution_number = RESOLUTION_MAP[resolution]
        print(resolution_number)

        # Resolucion
        winreg.SetValueEx(
            key,
            "Resolution",
            0,
            winreg.REG_DWORD,
            resolution_number
        )
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"No se pudo escribir en el registro\n{e}"
        )

def launch_game(server, windowed, resolution):
    
    # Validaciones
    if server not in SERVER_FILES:
        messagebox.showerror("Error", "Servidor inválido")
        return

    src = SERVER_FILES[server]

    if not src.exists():
        messagebox.showerror(
            "Error",
            f"No existe el archivo:\n{src}"
        )
        return

    if not MAIN_EXE.exists():
        messagebox.showerror(
            "Error",
            f"No se encontró main.exe en:\n{MU_PATH}"
        )
        return

    # 1️⃣ Copiar ServerInfo.sse
    try:
        shutil.copy(src, DEST_SERVERINFO)
    except Exception as e:
        messagebox.showerror("Error", f"Error copiando ServerInfo.sse\n{e}")
        return

    # 2️⃣ Configurar modo ventana y resolucion
    set_window_mode(windowed)
    set_window_resolution(resolution)

    # 3️⃣ Ejecutar MU
    try:
        subprocess.Popen(str(MAIN_EXE), cwd=str(MU_PATH))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo ejecutar el juego\n{e}")
        return
