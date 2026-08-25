import sys
import requests
from pathlib import Path

from const.config import API_URL, API_KEY, BASE_DIR, VERSION
from utils.logger import logger

def _extract_url(value):
    if not isinstance(value, str):
        return None
    if value.startswith("[") and "](" in value and value.endswith(")"):
        value = value[value.find("](") + 2:-1]
    return value if value.startswith(("http://", "https://")) else None

def _download_file(url, destination, headers, progress_callback=None, message="Descargando"):
    logger.info(f"Iniciando descarga: url={url}, destino={Path(destination).resolve()}")
    response = requests.get(url, headers=headers, stream=True, timeout=30)
    response.raise_for_status()
    total_bytes = int(response.headers.get("content-length", 0))
    downloaded_bytes = 0
    logger.info(f"Descarga aceptada: status={response.status_code}, bytes esperados={total_bytes or 'desconocidos'}")

    with open(destination, "wb") as output_file:
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            output_file.write(chunk)
            downloaded_bytes += len(chunk)
            if progress_callback and total_bytes:
                progress_callback(message, min(downloaded_bytes / total_bytes, 1.0))
    logger.info(f"Descarga finalizada: destino={Path(destination).resolve()}, bytes={downloaded_bytes}")

def check_and_update_launcher(progress_callback=None):
    """
    Verifica al inicio de la aplicación si existe una versión más reciente del launcher en el servidor.
    Si existe, la descarga a data/temp/new_launcher.exe e invoca al updater.
    """
    headers = {
        "x-api-key": API_KEY
    }
    launcher_url = f"{API_URL}/api/v2/launcher"
    try:
        logger.info(f"Iniciando chequeo del launcher: url={launcher_url}, version={VERSION}")
        logger.info(f"Directorio base: {BASE_DIR.resolve()}")
        if progress_callback:
            progress_callback("Verificando actualizaciones", None)
        response = requests.get(
            launcher_url,
            params={"version": VERSION},
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        launcher_info = response.json()
        logger.info(
            "Payload recibido: "
            f"name={launcher_info.get('name')}, version={launcher_info.get('version')}, "
            f"needUpdate={launcher_info.get('needUpdate')}"
        )
        if not getattr(sys, "frozen", False):
            print(f"[launcher] Respuesta de actualización: {launcher_info}")
        register_url = _extract_url(launcher_info.get("registerUrl"))
        if register_url:
            launcher_info["registerUrl"] = register_url

        if not launcher_info.get("needUpdate", False):
            logger.info("El launcher ya está actualizado; no se descargará ningún archivo.")
            if progress_callback:
                progress_callback("Launcher actualizado", 1.0)
            if not getattr(sys, "frozen", False):
                print("[launcher] No se necesita actualizar el launcher.")
            return launcher_info

        file_url = _extract_url(launcher_info.get("launcherUrl"))
        if not file_url:
            raise ValueError("La respuesta de actualización no contiene launcherUrl")
        logger.info(f"URL del launcher recibida: {file_url}")

        if launcher_info.get("name", "launcher.exe").lower() != "launcher.exe":
            logger.warning("El endpoint devolvió un archivo distinto de launcher.exe")
            return

        # Ruta actual del ejecutable del launcher
        if getattr(sys, 'frozen', False):
            current_exe = Path(sys.executable)
        else:
            current_exe = BASE_DIR / "launcher.exe"
        logger.info(f"Ejecutable actual: {current_exe.resolve()}, existe={current_exe.exists()}")

        logger.info("Nueva versión del launcher detectada. Descargando actualización...")
        if progress_callback:
            progress_callback("Descargando actualización", None)
        if not getattr(sys, "frozen", False):
            print(f"[launcher] Descargando actualización desde: {file_url}")
        temp_dir = BASE_DIR / "data" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        new_launcher_path = temp_dir / "new_launcher.exe"
        logger.info(f"Destino temporal del launcher: {new_launcher_path.resolve()}")

        _download_file(
            file_url,
            new_launcher_path,
            headers,
            progress_callback,
            "Descargando actualización",
        )

        updater_path = BASE_DIR / "updater.exe"
        updater_exists = updater_path.exists()
        logger.info(
            f"Comprobando updater: ruta={updater_path.resolve()}, existe={updater_exists}, "
            f"modo_compilado={getattr(sys, 'frozen', False)}"
        )
        if getattr(sys, "frozen", False) and not updater_exists:
            updater_url = _extract_url(launcher_info.get("updaterUrl"))
            if not updater_url:
                raise ValueError("No se encontró updater.exe ni updaterUrl")
            logger.info(f"URL del updater recibida: {updater_url}")
            logger.info("updater.exe no encontrado. Descargando actualizador...")
            if progress_callback:
                progress_callback("Descargando actualizador", None)
            if not getattr(sys, "frozen", False):
                print(f"[launcher] Descargando updater desde: {updater_url}")
            _download_file(updater_url, updater_path, headers, progress_callback, "Descargando actualizador")
            logger.info(f"Verificación posterior del updater: existe={updater_path.exists()}, ruta={updater_path.resolve()}")
            if not getattr(sys, "frozen", False):
                print(f"[launcher] Updater descargado: {updater_path}")
        elif not getattr(sys, "frozen", False):
            logger.info("Modo desarrollo: se utilizará updater.updater como módulo.")
        else:
            logger.info("updater.exe ya está presente; no se descargará.")

        launcher_info["_new_launcher_path"] = str(new_launcher_path)
        launcher_info["_current_exe"] = str(current_exe)
        launcher_info["_updater_path"] = str(updater_path) if updater_path.exists() else None
        if not getattr(sys, "frozen", False):
            print(f"[launcher] Descarga completada: {new_launcher_path}")
        return launcher_info

    except Exception as e:
        logger.error(f"Error al verificar actualización del launcher al inicio: {e}", exc_info=True)
        if not getattr(sys, "frozen", False):
            print(f"[launcher] Error durante el chequeo inicial: {e}")
        return None
