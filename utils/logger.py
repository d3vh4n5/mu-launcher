import os
import sys
import logging
import threading

# Directorio de logs
LOGS_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "launcher.log")

# Configuración del logger
logger = logging.getLogger("MuLauncher")
logger.setLevel(logging.INFO)

# Evitar handlers duplicados si se importa múltiples veces
if not logger.handlers:
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para guardar en archivo (logs/launcher.log)
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para mostrar en consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """Captura excepciones no manejadas en el hilo principal."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Excepción no capturada en el hilo principal:", exc_info=(exc_type, exc_value, exc_traceback))

def handle_thread_exception(args):
    """Captura excepciones no manejadas en hilos secundarios (threading)."""
    logger.critical(
        f"Excepción no capturada en el hilo '{args.thread.name}':",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
    )

def setup_exception_logging():
    """Registra hooks globales para capturar todos los errores en el archivo de log."""
    sys.excepthook = handle_uncaught_exception
    if hasattr(threading, "excepthook"):
        threading.excepthook = handle_thread_exception
