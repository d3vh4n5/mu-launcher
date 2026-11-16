"""
Tareas que se repiten mientras el launcher está abierto (noticias, actualizaciones).

El trabajo de red corre en un hilo aparte; el resultado se aplica en el hilo de tk.
La próxima ejecución se agenda recién cuando termina la anterior, así nunca se
pisan dos consultas iguales aunque la red esté lenta.
"""
import threading

from utils.logger import logger


def run_periodically(widget, interval_ms, work, on_result, first_delay_ms=None, name="periodic"):
    """
    Ejecuta work() en segundo plano cada interval_ms y pasa su resultado a
    on_result(result) en el hilo de tk. Si work() falla, on_result recibe None.
    first_delay_ms: cuánto esperar la primera vez (por defecto, interval_ms).
    """
    def tick():
        threading.Thread(target=worker, daemon=True, name=name).start()

    def worker():
        try:
            result = work()
        except Exception as e:
            logger.error(f"Tarea periódica {name} falló: {e}")
            result = None
        try:
            widget.after(0, done, result)
        except Exception:
            pass  # la ventana se cerró mientras trabajaba

    def done(result):
        try:
            if not widget.winfo_exists():
                return
            on_result(result)
        except Exception as e:
            logger.error(f"Tarea periódica {name}: error al aplicar el resultado: {e}")
        finally:
            try:
                widget.after(interval_ms, tick)
            except Exception:
                pass

    widget.after(interval_ms if first_delay_ms is None else first_delay_ms, tick)
