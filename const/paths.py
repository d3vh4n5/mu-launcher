"""
Rutas del launcher. Sin dependencias para que lo puedan importar el launcher,
el logger y el updater.

- Lo que se distribuye (va en el manifest) vive en la carpeta del cliente:
    <cliente>/Data/Launcher/
- Lo que genera la PC (temp, logs) vive fuera del cliente, por usuario:
    %LOCALAPPDATA%/MuCampana/
  No requiere permisos de administrador y no se sincroniza con OneDrive.
"""
import os
import tempfile
from pathlib import Path

APP_FOLDER_NAME = "MuCampana"

# Carpeta del cliente (donde están main.exe y launcher.exe)
CLIENT_DIR = Path.cwd()

# Archivos del launcher que se distribuyen con el cliente
LAUNCHER_DATA_DIR = CLIENT_DIR / "Data" / "Launcher"
UPDATER_EXE = LAUNCHER_DATA_DIR / "updater.exe"


def _app_data_dir() -> Path:
    base = os.getenv("LOCALAPPDATA")
    if base:
        return Path(base) / APP_FOLDER_NAME
    # Muy raro en Windows, pero por las dudas
    return Path(tempfile.gettempdir()) / APP_FOLDER_NAME


# Archivos generados en runtime (nunca van al manifest)
APP_DATA_DIR = _app_data_dir()
TEMP_DIR = APP_DATA_DIR / "temp"
LOGS_DIR = APP_DATA_DIR / "logs"
NEW_LAUNCHER_EXE = TEMP_DIR / "new_launcher.exe"

# Ubicaciones viejas, para limpiarlas al migrar
LEGACY_TEMP_DIR = CLIENT_DIR / "Data" / "temp"
LEGACY_UPDATER_EXE = CLIENT_DIR / "updater.exe"


def ensure_runtime_dirs():
    for d in (TEMP_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)
