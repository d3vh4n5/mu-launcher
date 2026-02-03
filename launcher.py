import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import shutil
import subprocess
import winreg


# =========================
# CONFIGURACIÓN
# =========================


# Mapeo de resoluciones a como las necesito en el regedit
RESOLUTION_MAP = {
    "640 x 480": 0,
    "800 x 600": 1,
    "1024 x 768": 2,
    "1280 x 1024": 3,
}

# Carpeta donde está ESTE launcher
BASE_DIR = Path.cwd()

# Ruta al cliente MU
MU_PATH = BASE_DIR

# Ejecutable principal
MAIN_EXE = MU_PATH / "main.exe"

# ServerInfo disponibles
SERVER_FILES = {
    "Local": MU_PATH / "serverinfo/ServerInfo_local.sse",
    "Online": MU_PATH / "serverinfo/ServerInfo_online.sse",
}
# Archivo destino en el cliente
DEST_SERVERINFO = MU_PATH / "ServerInfo.sse"

# Archivo de configuración gráfica
MAININFO_INI = MU_PATH / "MainInfo.ini"

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

def set_window_resolution(resolution: int):
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

def launch_game():
    server = server_var.get()
    windowed = window_var.get()
    resolution = resolution_var.get()

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

    root.destroy()


# =========================
# UI
# =========================

root = tk.Tk()
root.title("MU Launcher")
root.geometry("300x420")
root.resizable(False, False)

# Título
tk.Label(
    root,
    text="MU Online Launcher",
    font=("Arial", 14, "bold")
).pack(pady=10)

# Selector de servidor
tk.Label(root, text="Servidor").pack()
server_var = tk.StringVar(value="Online")

ttk.Combobox(
    root,
    textvariable=server_var,
    values=list(SERVER_FILES.keys()),
    state="readonly",
    width=20
).pack(pady=5)

# Modo ventana
window_var = tk.BooleanVar(value=True)
tk.Checkbutton(
    root,
    text="Modo ventana",
    variable=window_var
).pack(pady=10)

# resolucion
tk.Label(root, text="Resolución").pack()

resolution_var = tk.StringVar(value="800 x 600")

ttk.Combobox(
    root,
    textvariable=resolution_var,
    values=list(RESOLUTION_MAP.keys()),
    state="readonly",
    width=20
).pack(pady=5)


# Botón jugar
tk.Button(
    root,
    text="JUGAR",
    width=20,
    height=2,
    command=launch_game
).pack(pady=15)

root.mainloop()
