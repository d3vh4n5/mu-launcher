"""
Preferencias propias del launcher. Se guardan en HKCU\\Software\\MuCampana\\Launcher,
separadas de Software\\Webzen\\MU\\config, que es la configuración del juego.
"""
import winreg

from utils.logger import logger

_KEY = r"Software\MuCampana\Launcher"

# Qué hace la X de la ventana principal
CLOSE_TO_TRAY = "tray"  # se oculta y queda en el área de notificación (como Steam)
CLOSE_EXIT = "exit"     # cierra el launcher
CLOSE_ACTIONS = (CLOSE_TO_TRAY, CLOSE_EXIT)
DEFAULT_CLOSE_ACTION = CLOSE_TO_TRAY


def _get(name, default=None):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _KEY) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except OSError:
        return default


def _set(name, value, reg_type=winreg.REG_SZ):
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _KEY) as key:
            winreg.SetValueEx(key, name, 0, reg_type, value)
    except OSError as e:
        logger.error(f"No se pudo guardar la preferencia {name}: {e}")


def get_close_action():
    value = _get("CloseAction", DEFAULT_CLOSE_ACTION)
    return value if value in CLOSE_ACTIONS else DEFAULT_CLOSE_ACTION


def set_close_action(value):
    if value in CLOSE_ACTIONS:
        _set("CloseAction", value)


def tray_hint_shown():
    return _get("TrayHintShown", 0) == 1


def set_tray_hint_shown():
    _set("TrayHintShown", 1, winreg.REG_DWORD)
