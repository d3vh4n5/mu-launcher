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

# Evento con el que una segunda instancia le pide a la primera que muestre su ventana
# (por ejemplo, si quedó oculta en la bandeja y el usuario abre launcher.exe otra vez).
_SHOW_EVENT_NAME = "Local\\MuCampanaLauncher_Show"
_EVENT_MODIFY_STATE = 0x0002
_SYNCHRONIZE = 0x00100000
_INFINITE = 0xFFFFFFFF
_WAIT_OBJECT_0 = 0


def signal_running_instance():
    """Pide a la instancia que ya corre que muestre su ventana. True si la encontró."""
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenEventW(_EVENT_MODIFY_STATE, False, _SHOW_EVENT_NAME)
        if not handle:
            return False
        try:
            return bool(kernel32.SetEvent(handle))
        finally:
            kernel32.CloseHandle(handle)
    except Exception:
        return False


def listen_for_show_requests(callback):
    """
    Llama a callback() (desde un hilo aparte) cada vez que otra instancia lo pide.
    El callback no debe tocar tkinter directamente: usar root.after().
    """
    import threading

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateEventW(None, False, False, _SHOW_EVENT_NAME)  # auto-reset
    if not handle:
        return

    def wait_loop():
        while kernel32.WaitForSingleObject(handle, _INFINITE) == _WAIT_OBJECT_0:
            try:
                callback()
            except Exception:
                pass

    threading.Thread(target=wait_loop, daemon=True, name="show-requests").start()


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

