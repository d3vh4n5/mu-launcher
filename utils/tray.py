"""
Ícono del launcher en el área de notificación (bandeja del sistema).

pystray corre en su propio hilo y, después de cada acción del menú, vuelve a
evaluar los textos del menú. Ese hilo NUNCA debe tocar tkinter (ni root.after ni
variables de tk): si la ventana ya se cerró, la llamada queda esperando al hilo
principal para siempre y el proceso no termina. Por eso:
  - los pedidos del menú se encolan y los ejecuta el hilo de tkinter (_poll);
  - los textos se leen de una copia en Python puro (set_lang), no de un StringVar.
"""
import base64
import io
import queue

from assets.icono_data import ICONO_BASE64
from const.texts import TEXTS
from utils.logger import logger

_POLL_MS = 100


class TrayIcon:
    def __init__(self, root, title, lang="Spn", on_play=None):
        """
        root: ventana principal. lang: idioma inicial del menú (actualizar con set_lang).
        on_play: se llama (en el hilo de tkinter) al elegir "Jugar" en el menú.
        Crear desde el hilo de tkinter.
        """
        self.root = root
        self.on_play = on_play
        self._lang = lang
        self._icon = None
        self._queue = queue.Queue()
        self._closed = False
        self._poll()

        try:
            import pystray
            from PIL import Image
        except Exception as e:
            logger.error(f"Bandeja del sistema no disponible: {e}")
            return

        try:
            image = Image.open(io.BytesIO(base64.b64decode(ICONO_BASE64)))
            menu_items = [
                pystray.MenuItem(
                    lambda item: self._txt("tray_open", "Abrir launcher"),
                    lambda icon, item: self.post(self.show),
                    default=True,  # clic sobre el ícono
                ),
            ]
            if on_play:
                menu_items.append(pystray.MenuItem(
                    lambda item: self._txt("play", "JUGAR").strip().capitalize(),
                    lambda icon, item: self.post(self.on_play),
                ))
            menu_items += [
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    lambda item: self._txt("tray_exit", "Salir"),
                    lambda icon, item: self.post(self.quit),
                ),
            ]
            self._icon = pystray.Icon("MuCampanaLauncher", image, title, pystray.Menu(*menu_items))
            self._icon.run_detached()
        except Exception as e:
            logger.error(f"No se pudo crear el ícono de la bandeja: {e}", exc_info=True)
            self._icon = None

    @property
    def available(self):
        return self._icon is not None

    # ------------------------------------------------- seguro desde cualquier hilo
    def post(self, fn):
        """Pide ejecutar fn en el hilo de tkinter. Se puede llamar desde cualquier hilo."""
        if not self._closed:
            self._queue.put(fn)

    def set_lang(self, lang):
        self._lang = lang

    def _txt(self, key, fallback):
        return TEXTS.get(self._lang, TEXTS["Spn"]).get(key, fallback)

    # ----------------------------------------------------- solo hilo de tkinter
    def _poll(self):
        if self._closed:
            return
        while True:
            try:
                fn = self._queue.get_nowait()
            except queue.Empty:
                break
            try:
                fn()
            except Exception as e:
                logger.error(f"Error en acción de la bandeja: {e}", exc_info=True)
            if self._closed:
                return
        self.root.after(_POLL_MS, self._poll)

    def show(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide(self):
        """Oculta la ventana; el launcher sigue vivo en la bandeja."""
        if not self.available:
            self.root.iconify()  # sin bandeja, minimizar para no perder la ventana
            return
        self.root.withdraw()

    def notify(self, message, title=None):
        if not self.available:
            return
        try:
            self._icon.notify(message, title)
        except Exception as e:
            logger.debug(f"No se pudo mostrar la notificación: {e}")

    def stop(self):
        self._closed = True
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def quit(self):
        self.stop()
        try:
            self.root.destroy()
        except Exception:
            pass
