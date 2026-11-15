from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Compilado: el .env va embebido en el exe (launcher.spec -> datas) y PyInstaller
# lo extrae en sys._MEIPASS. En desarrollo se usa el .env de la carpeta actual.
if getattr(sys, "frozen", False):
    env_file = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)) / ".env"
else:
    env_file = Path.cwd() / ".env"
load_dotenv(dotenv_path=env_file)

PROJECT_NAME="Mu Campana"
VERSION="1.2.8"
REGISTER_URL= "https://mu-front.vercel.app/register"
MU_SERVER_URL= os.getenv("MU_SERVER_URL")
API_URL= os.getenv("API_URL")
API_KEY = os.getenv("API_KEY") #Campiar por la api key al momento de compilar

# Debe coincidir con LauncherMutex de MainInfo.ini (máx. 31 caracteres).
# Con LauncherStart = 1, Main.dll cierra main.exe si este mutex no existe.
LAUNCHER_MUTEX = "MuCampanaLauncherMtx"
# =========================
# CONFIGURACIÓN
# =========================
app_width=300
app_heigh=630
components_width=250

RESOLUTION_MAP = {
    "640 x 480": 0,
    "800 x 600": 1,
    "1024 x 768": 2,
    "1280 x 1024": 3,
    # --- Formatos modernos ---
    "1366 x 768": 4,   # Laptop estándar
    "1440 x 900": 5,   # 16:10 Proporción
    "1600 x 900": 6,   # HD+
    "1920 x 1080": 7,  # Full HD (Muy común)
    "2560 x 1440": 8,  # 2K / QHD
    #"3840 x 2160": 9,  # 4K Ultra HD
}
from const.paths import CLIENT_DIR, LAUNCHER_DATA_DIR

# Carpeta donde está ESTE launcher
BASE_DIR = CLIENT_DIR

# Ruta al cliente MU
MU_PATH = BASE_DIR

# Ejecutable principal
MAIN_EXE = MU_PATH / "main.exe"

# ServerInfo disponibles
SERVER_FILES = {
    "Local": LAUNCHER_DATA_DIR / "serverinfo/ServerInfo_local.sse",
    "Online": LAUNCHER_DATA_DIR / "serverinfo/ServerInfo_online.sse",
}
# Archivo destino en el cliente
DEST_SERVERINFO = MU_PATH / "ServerInfo.sse"

# Archivo de configuración gráfica
MAININFO_INI = MU_PATH / "MainInfo.ini"