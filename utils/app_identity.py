"""
Identidad del launcher para Windows (AppUserModelID).

Sin esto, Windows agrupa el proceso como "Python" y así lo muestra en las
notificaciones de la bandeja. Se registra el nombre y el ícono en HKCU (no hace
falta admin) y se asigna el ID al proceso. Llamar al inicio, antes de crear ventanas.
"""
import base64
import ctypes
import winreg

from assets.icono_data import ICONO_BASE64
from const.config import PROJECT_NAME
from const.paths import APP_DATA_DIR
from utils.logger import logger

APP_ID = "MuCampana.Launcher"


def register_app_identity():
    try:
        icon_path = APP_DATA_DIR / "launcher.ico"
        icon_path.parent.mkdir(parents=True, exist_ok=True)
        icon_path.write_bytes(base64.b64decode(ICONO_BASE64))

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\AppUserModelId\{APP_ID}") as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, PROJECT_NAME)
            winreg.SetValueEx(key, "IconUri", 0, winreg.REG_SZ, str(icon_path))

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception as e:
        logger.warning(f"No se pudo registrar la identidad del launcher: {e}")
