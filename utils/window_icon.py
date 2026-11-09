import base64
import os
import tempfile

from assets.icono_data import ICONO_BASE64

_ICON_PATH = os.path.join(tempfile.gettempdir(), "mu_campana_icon.ico")


def get_icon_path() -> str:
    """Escribe el ícono embebido a un archivo temporal y devuelve su ruta."""
    with open(_ICON_PATH, "wb") as tmp:
        tmp.write(base64.b64decode(ICONO_BASE64))
    return _ICON_PATH


def set_window_icon(window, delay_ms: int = 0) -> None:
    """
    Aplica el ícono de MU Campana a una ventana tk/customtkinter.

    CTkToplevel pone su propio ícono a los 200 ms de crearse, así que para
    ventanas secundarias hay que pasar delay_ms > 200 para que no lo pise.
    """

    def apply():
        try:
            window.iconbitmap(get_icon_path())
        except Exception as error:
            print(f"No se pudo aplicar el ícono: {error}")

    if delay_ms > 0:
        window.after(delay_ms, apply)
    else:
        apply()
