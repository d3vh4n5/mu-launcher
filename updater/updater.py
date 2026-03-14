from const.config import BASE_DIR
from updater.process import force_close_launcher
from updater.files import update_executable
from updater.logger import log_message

def update():
    # 1 - Ver que el proceso del launcher terminó
    try:
        # Lo mato o espero que termine? https://psutil.readthedocs.io/en/latest/#psutil.wait_procs
        force_close_launcher('launcher.exe')
    except Exception as e:
        log_message(f"Error al intentar terminar el proceso: {e}")
    # 2 - Verificar que el nuevo launcher esté en la carpeta de descargas

    # 3 - Verificar que la descarga se completó (comparar hash)
    # 4 - Reemplazar el launcher viejo por el nuevo
    new_launcher_path = BASE_DIR / "data/launcher/launcher-1234.exe"
    launcher_path = BASE_DIR / 'launcher.exe'
    log_message(f"Reemplazando {launcher_path} por {new_launcher_path}...")

    update_executable(launcher_path, new_launcher_path)


    #--- Para desarrollo ---
    log_message("Actualización completada con éxito.")
    input("Presiona Enter para cerrar esta ventana...")