from pathlib import Path

PROJECT_NAME="Mu Campana"
VERSION="1.2.2"
REGISTER_URL= "https://mu-front.vercel.app/register"
API_URL="http://localhost:3000"
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
# Carpeta donde está ESTE launcher
BASE_DIR = Path.cwd()

# Ruta al cliente MU
MU_PATH = BASE_DIR

# Ejecutable principal
MAIN_EXE = MU_PATH / "main.exe"

# ServerInfo disponibles
SERVER_FILES = {
    "Local": MU_PATH / "serverinfo/ServerInfo_local.sse",
    "Online": MU_PATH / "serverinfo/ServerInfo_online.sse",
}
# Archivo destino en el cliente
DEST_SERVERINFO = MU_PATH / "ServerInfo.sse"

# Archivo de configuración gráfica
MAININFO_INI = MU_PATH / "MainInfo.ini"