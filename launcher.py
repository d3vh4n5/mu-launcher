import utils.wmi_guard  # noqa: F401  (debe ir antes de customtkinter)
from tkinter import messagebox

from views.app import App
from utils.process import process_exists, signal_running_instance
from utils.logger import logger, setup_exception_logging
from utils.app_identity import register_app_identity
from views.startup_window import start_application

if __name__ == "__main__":
    setup_exception_logging()

    if process_exists('launcher.exe'):
        # Si la otra instancia está en la bandeja, se le pide que muestre su ventana
        if signal_running_instance():
            logger.info("El launcher ya está abierto: se pidió mostrar su ventana.")
        else:
            logger.warning("Intento de apertura duplicada: El launcher ya está en ejecución.")
            messagebox.showinfo("Proceso", "El proceso ya está en ejecución.")
    else:
        try:
            register_app_identity()  # nombre "Mu Campana" en notificaciones (no "Python")
            start_application()
        except Exception as e:
            logger.critical(f"Error fatal al iniciar la aplicación: {e}", exc_info=True)
            messagebox.showerror("Error", f"Ocurrió un error inesperado al iniciar el launcher:\n{e}")


