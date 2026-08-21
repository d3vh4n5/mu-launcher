from views.app import App
from utils.process import process_exists
from utils.logger import logger, setup_exception_logging
from tkinter import messagebox

if __name__ == "__main__":
    setup_exception_logging()
    logger.info("Iniciando Launcher...")

    if process_exists('launcher.exe'):
        logger.warning("Intento de apertura duplicada: El launcher ya está en ejecución.")
        messagebox.showinfo("Proceso", "El proceso ya está en ejecución.")
    else:
        try:
            App()
        except Exception as e:
            logger.critical(f"Error fatal al iniciar la aplicación: {e}", exc_info=True)
            messagebox.showerror("Error", f"Ocurrió un error inesperado al iniciar el launcher:\n{e}")


