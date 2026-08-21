import os
import sys
import ctypes
import subprocess

_mutex_handle = None

def is_already_running(app_id="Global\\MuLauncher_SingleInstance_Mutex"):
    """
    Verifica si ya existe otra instancia del launcher ejecutándose en el sistema
    mediante un Mutex de Windows.
    """
    global _mutex_handle
    try:
        kernel32 = ctypes.windll.kernel32
        _mutex_handle = kernel32.CreateMutexW(None, False, app_id)
        last_error = kernel32.GetLastError()
        # ERROR_ALREADY_EXISTS = 183
        if last_error == 183:
            return True
        return False
    except Exception:
        return False

def process_exists(process_name):
    """
    Verifica si un proceso está en ejecución.
    Si se comprueba la instancia del propio launcher, se usa el Mutex de Windows
    para evitar falsos positivos con el propio proceso en ejecución.
    """
    current_exe = os.path.basename(sys.executable).lower()
    name_lower = process_name.lower()

    if name_lower in ("launcher.exe", "launcher.py", current_exe):
        return is_already_running()

    try:
        # Flag 0x08000000 es CREATE_NO_WINDOW
        output = subprocess.check_output('tasklist', creationflags=0x08000000).decode('utf-8', errors='ignore')
        return name_lower in output.lower()
    except Exception:
        return False

