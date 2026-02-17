import time
from tkinter import ttk, messagebox
import shutil
import subprocess
import winreg
import webbrowser

from const.config import *
from const.texts import TEXTS

# =========================
# FUNCIONES
# =========================

def get_registry_value(clave):
    route = r"Software\Webzen\MU\config"
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(reg, route)
        valor, tipo = winreg.QueryValueEx(key, clave)
        winreg.CloseKey(key)
        return valor
    except (FileNotFoundError, OSError):
        return False

def set_reg_dword(var_name, var_value, reg_type = "REG_DWORD"):
    try:
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Webzen\MU\config"
        )

        winreg.SetValueEx(
            key,
            var_name,
            0,
            winreg.REG_DWORD 
                if reg_type == "REG_DWORD" 
                else winreg.REG_SZ,
            var_value
        )
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"No se pudo escribir en el registro\n{e}"
        )


def launch_game(server, windowed, resolution, audio, music, volume, lang, btn_play, root):
    btn_play.configure(state="disabled", text="Lanzando..") # Evitar múltiples clicks
    root.update()
    
    # Ejecutar MU
    try:
        set_reg_dword("WindowMode", windowed)
        resolution_number = RESOLUTION_MAP[resolution]
        set_reg_dword("Resolution", resolution_number)
        set_reg_dword("SoundOnOff", audio)
        set_reg_dword("MusicOnOff", music)
        set_reg_dword("VolumeLevel", volume)
        set_reg_dword("LangSelection", lang, "REG_SZ")

        # Validaciones
        if not MAIN_EXE.exists():
            messagebox.showerror(
                "Error",
                f"No se encontró main.exe en:\n{MU_PATH}"
            )
            return
        subprocess.Popen(str(MAIN_EXE), cwd=str(MU_PATH))

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo ejecutar el juego\n{e}")

        return
    finally:
        #btn_play.configure(state="normal", text=TEXTS[lang]["play"])
        root.after(2000, lambda: btn_play.configure(state="normal", text=TEXTS[lang]["play"]))

def abrir_enlace(event):
    url = REGISTER_URL
    webbrowser.open(url)