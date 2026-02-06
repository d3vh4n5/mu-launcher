from tkinter import ttk, messagebox
import shutil
import subprocess
import winreg
import webbrowser

from const.config import *

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


def launch_game(server, windowed, resolution, audio, music, volume, lang):
    set_reg_dword("WindowMode", windowed)
    resolution_number = RESOLUTION_MAP[resolution]
    set_reg_dword("Resolution", resolution_number)
    set_reg_dword("SoundOnOff", audio)
    set_reg_dword("MusicOnOff", music)
    set_reg_dword("VolumeLevel", volume)
    set_reg_dword("LangSelection", lang, "REG_SZ")
    # Validaciones

    # if server not in SERVER_FILES:
    #     messagebox.showerror("Error", "Servidor inválido")
    #     return

    # src = SERVER_FILES[server]

    # if not src.exists():
    #     messagebox.showerror(
    #         "Error",
    #         f"No existe el archivo:\n{src}"
    #     )
    #     return

    if not MAIN_EXE.exists():
        messagebox.showerror(
            "Error",
            f"No se encontró main.exe en:\n{MU_PATH}"
        )
        return

    # Copiar ServerInfo.sse
    # try:
    #     shutil.copy(src, DEST_SERVERINFO)
    # except Exception as e:
    #     messagebox.showerror("Error", f"Error copiando ServerInfo.sse\n{e}")
    #     return


    # Ejecutar MU
    try:
        subprocess.Popen(str(MAIN_EXE), cwd=str(MU_PATH))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo ejecutar el juego\n{e}")
        return

def abrir_enlace(event):
    url = "https://mu-front.vercel.app/register"
    webbrowser.open(url)