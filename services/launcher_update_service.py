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
        if not getattr(sys, "frozen", False):
            print(f"[launcher] Respuesta de actualización: {launcher_info}")
        register_url = _extract_url(launcher_info.get("registerUrl"))
        if register_url:
            launcher_info["registerUrl"] = register_url

        if not launcher_info.get("needUpdate", False):
            if progress_callback:
                progress_callback("Launcher actualizado", 1.0)
            if not getattr(sys, "frozen", False):
                print("[launcher] No se necesita actualizar el launcher.")
            return launcher_info

        file_url = _extract_url(launcher_info.get("fileUrl"))
        if not file_url:
            raise ValueError("La respuesta de actualización no contiene fileUrl")

        if launcher_info.get("name", "launcher.exe").lower() != "launcher.exe":
            logger.warning("El endpoint devolvió un archivo distinto de launcher.exe")
            return

        # Ruta actual del ejecutable del launcher
        if getattr(sys, 'frozen', False):
            current_exe = Path(sys.executable)
        else:
            current_exe = BASE_DIR / "launcher.exe"

        logger.info("Nueva versión del launcher detectada. Descargando actualización...")
        if progress_callback:
            progress_callback("Descargando actualización", None)
        if not getattr(sys, "frozen", False):
            print(f"[launcher] Descargando actualización desde: {file_url}")
        temp_dir = BASE_DIR / "data" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        new_launcher_path = temp_dir / "new_launcher.exe"

        file_response = requests.get(file_url, headers=headers, stream=True, timeout=30)
        file_response.raise_for_status()

        with open(new_launcher_path, "wb") as launcher_file:
            total_bytes = int(file_response.headers.get("content-length", 0))
            downloaded_bytes = 0
            for chunk in file_response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                launcher_file.write(chunk)
                downloaded_bytes += len(chunk)
                if progress_callback and total_bytes:
                    progress_callback(
                        "Descargando actualización",
                        min(downloaded_bytes / total_bytes, 1.0),
                    )

        launcher_info["_new_launcher_path"] = str(new_launcher_path)
        launcher_info["_current_exe"] = str(current_exe)
        if not getattr(sys, "frozen", False):
            print(f"[launcher] Descarga completada: {new_launcher_path}")
        return launcher_info

    except Exception as e:
        logger.error(f"Error al verificar actualización del launcher al inicio: {e}")
        if not getattr(sys, "frozen", False):
            print(f"[launcher] Error durante el chequeo inicial: {e}")
        return None
