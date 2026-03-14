import ctypes
import sys
import os

def is_admin():
    try:
        # Intenta realizar una acción que solo un admin puede hacer
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Solicitando permisos de administrador...")
    # Re-ejecuta el script actual pidiendo privilegios
    # 'runas' es el verbo mágico en Windows para disparar el UAC
    ctypes.windll.shell32.ShellExecuteW(
        None, 
        "runas", 
        sys.executable, 
        " ".join(sys.argv), 
        None, 
        1
    )
    sys.exit()