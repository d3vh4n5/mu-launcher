from tkinter import messagebox

from views.app import App
from utils.process import process_exists
from utils.logger import logger, setup_exception_logging
from views.startup_window import start_application

if __name__ == "__main__":
    setup_exception_logging()

    if process_exists('launcher.exe'):
        logger.warning("Intento de apertura duplicada: El launcher ya está en ejecución.")
        messagebox.showinfo("Proceso", "El proceso ya está en ejecución.")
    else:
        try:
            start_application()
        except Exception as e:
            logger.critical(f"Error fatal al iniciar la aplicación: {e}", exc_info=True)
            messagebox.showerror("Error", f"Ocurrió un error inesperado al iniciar el launcher:\n{e}")


