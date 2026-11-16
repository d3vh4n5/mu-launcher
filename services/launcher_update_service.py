import sys
import shutil
import hashlib
import requests
from pathlib import Path

from const.config import API_URL, API_KEY, BASE_DIR, VERSION
from const.paths import (
    TEMP_DIR, NEW_LAUNCHER_EXE, UPDATER_EXE,
    LEGACY_TEMP_DIR, LEGACY_UPDATER_EXE, ensure_runtime_dirs,
)
from utils.logger import logger


def cleanup_runtime_files():
    """
    Borra restos de actualizaciones anteriores y migra desde las ubicaciones viejas
    (Data/temp y updater.exe en la raíz del cliente). Nunca debe cortar el inicio.
    """
    try:
        if NEW_LAUNCHER_EXE.exists():
            NEW_LAUNCHER_EXE.unlink()
            logger.info(f"Borrado launcher temporal de una actualización anterior: {NEW_LAUNCHER_EXE}")
    except Exception as e:
        logger.warning(f"No se pudo borrar {NEW_LAUNCHER_EXE}: {e}")

    try:
        if LEGACY_TEMP_DIR.exists():
            shutil.rmtree(LEGACY_TEMP_DIR)
            logger.info(f"Borrada carpeta temporal vieja: {LEGACY_TEMP_DIR}")
    except Exception as e:
        logger.warning(f"No se pudo borrar {LEGACY_TEMP_DIR}: {e}")

    try:
        if LEGACY_UPDATER_EXE.exists():
            if UPDATER_EXE.exists():
                LEGACY_UPDATER_EXE.unlink()
                logger.info(f"Borrado updater viejo de la raíz: {LEGACY_UPDATER_EXE}")
            else:
                UPDATER_EXE.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(LEGACY_UPDATER_EXE), str(UPDATER_EXE))
                logger.info(f"Updater movido a {UPDATER_EXE}")
    except Exception as e:
        logger.warning(f"No se pudo migrar {LEGACY_UPDATER_EXE}: {e}")

def _extract_url(value):
    if not isinstance(value, str):
        return None
    if value.startswith("[") and "](" in value and value.endswith(")"):
        value = value[value.find("](") + 2:-1]
    return value if value.startswith(("http://", "https://")) else None

def _sha256_of(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def _download_file(url, destination, headers, progress_callback=None, message="Descargando",
                   expected_sha256=None):
    """
    Descarga a un .part y solo lo deja en `destination` si el sha256 coincide con
    el que informó la API. Si no coincide (descarga cortada, archivo corrupto o
    alterado) se borra y se lanza ValueError: nunca se instala un exe a medias.
    """
    destination = Path(destination)
    part_path = destination.with_name(destination.name + ".part")
    logger.info(f"Iniciando descarga: url={url}, destino={destination.resolve()}")
    response = requests.get(url, headers=headers, stream=True, timeout=30)
    response.raise_for_status()
    total_bytes = int(response.headers.get("content-length", 0))
    downloaded_bytes = 0
    sha = hashlib.sha256()
    logger.info(f"Descarga aceptada: status={response.status_code}, bytes esperados={total_bytes or 'desconocidos'}")

    try:
        with open(part_path, "wb") as output_file:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                output_file.write(chunk)
                sha.update(chunk)
                downloaded_bytes += len(chunk)
                if progress_callback and total_bytes:
                    progress_callback(message, min(downloaded_bytes / total_bytes, 1.0))

        actual_sha256 = sha.hexdigest()
        if expected_sha256:
            if actual_sha256.lower() != expected_sha256.lower():
                raise ValueError(
                    f"El archivo descargado no es válido (sha256 {actual_sha256}, "
                    f"esperado {expected_sha256}, bytes={downloaded_bytes})"
                )
            logger.info(f"sha256 verificado: {actual_sha256}")
        else:
            logger.warning(f"La API no informó sha256 para {url}; se instala sin verificar")

        part_path.replace(destination)
    finally:
        if part_path.exists():
            part_path.unlink()
    logger.info(f"Descarga finalizada: destino={destination.resolve()}, bytes={downloaded_bytes}")

def fetch_launcher_info():
    """
    Solo consulta si hay una versión nueva del launcher, sin descargar nada.
    Devuelve el payload de la API ({needUpdate, version, ...}) o None si falló.
    """
    try:
        response = requests.get(
            f"{API_URL}/api/v2/launcher",
            params={"version": VERSION},
            headers={"x-api-key": API_KEY},
            timeout=10,
        )
        response.raise_for_status()
        info = response.json()
        return info if isinstance(info, dict) else None
    except Exception as e:
        logger.warning(f"No se pudo consultar la versión del launcher: {e}")
        return None


def check_and_update_launcher(progress_callback=None):
    """
    Verifica al inicio de la aplicación si existe una versión más reciente del launcher en el servidor.
    Si existe, la descarga a %LOCALAPPDATA%/MuCampana/temp/new_launcher.exe e invoca al updater.
    """
    headers = {
        "x-api-key": API_KEY
    }
    launcher_url = f"{API_URL}/api/v2/launcher"
    cleanup_runtime_files()
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
        ensure_runtime_dirs()
        new_launcher_path = NEW_LAUNCHER_EXE
        logger.info(f"Destino temporal del launcher: {new_launcher_path.resolve()}")

        _download_file(
            file_url,
            new_launcher_path,
            headers,
            progress_callback,
            "Descargando actualización",
            expected_sha256=launcher_info.get("launcherSha256"),
        )

        updater_path = UPDATER_EXE
        updater_path.parent.mkdir(parents=True, exist_ok=True)
        updater_sha256 = launcher_info.get("updaterSha256")
        # Si el updater local no coincide con el publicado (viejo o corrupto), se vuelve a bajar
        if updater_path.exists() and updater_sha256 and _sha256_of(updater_path) != updater_sha256.lower():
            logger.info("updater.exe local distinto del publicado; se descargará de nuevo.")
            updater_path.unlink()
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
            _download_file(updater_url, updater_path, headers, progress_callback, "Descargando actualizador",
                           expected_sha256=updater_sha256)
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
