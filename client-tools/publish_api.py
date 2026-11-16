"""Cliente HTTP de /api/v2/tools/client-publish (publicar el cliente sin RDP)."""
from urllib.parse import urlparse

import requests

TIMEOUT = 30
# Publicar re-verifica el cliente en el servidor y mueve miles de archivos:
# 10 s para conectar, hasta 10 min para la respuesta.
PUBLISH_TIMEOUT = (10, 600)
UPLOAD_ATTEMPTS = 3
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


class PublishApiError(Exception):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def is_insecure_url(url):
    """http:// a un servidor remoto: la API key viajaría sin cifrar."""
    parsed = urlparse(url)
    return parsed.scheme == "http" and parsed.hostname not in LOCAL_HOSTS


class PublishApi:
    def __init__(self, base_url, api_key):
        self.base = base_url.rstrip("/") + "/api/v2/tools/client-publish"
        self.api_key = api_key
        self.session = requests.Session()

    def _request(self, method, path, headers=None, timeout=TIMEOUT, **kwargs):
        all_headers = {"x-api-key": self.api_key, **(headers or {})}
        try:
            resp = self.session.request(
                method, self.base + path, headers=all_headers, timeout=timeout, **kwargs
            )
        except requests.exceptions.RequestException as e:
            raise PublishApiError(f"No se pudo conectar con el servidor: {e}") from e

        if not resp.ok:
            raise PublishApiError(self._error_message(resp), status=resp.status_code)
        return resp.json()

    @staticmethod
    def _error_message(resp):
        try:
            data = resp.json()
        except ValueError:
            return f"Error {resp.status_code}: {resp.text[:200]}"
        message = data.get("message", f"Error {resp.status_code}")
        if isinstance(message, list):
            message = "; ".join(map(str, message))
        problems = data.get("problems") or []
        if problems:
            shown = "\n".join(f"• {p}" for p in problems[:10])
            more = f"\n… y {len(problems) - 10} más" if len(problems) > 10 else ""
            message = f"{message}:\n{shown}{more}"
        return message

    def get_state(self):
        return self._request("GET", "/state")["files"]

    def create_session(self, force):
        params = {"force": "true" if force else "false"}
        return self._request("POST", "/sessions", params=params)["sessionId"]

    def cancel_session(self, session_id):
        self._request("DELETE", f"/sessions/{session_id}")

    def upload_file(self, session_id, rel_path, full_path, sha256):
        """Sube un archivo; reintenta solo ante cortes de red (no ante errores de la API)."""
        last_error = None
        for _ in range(UPLOAD_ATTEMPTS):
            try:
                with open(full_path, "rb") as fh:
                    return self._request(
                        "PUT",
                        f"/sessions/{session_id}/files",
                        headers={
                            "x-sha256": sha256,
                            "Content-Type": "application/octet-stream",
                        },
                        # params= codifica espacios y acentos en la URL
                        params={"path": rel_path},
                        data=fh,
                    )
            except PublishApiError as e:
                if not isinstance(e.__cause__, (requests.exceptions.ConnectionError,
                                                requests.exceptions.Timeout)):
                    raise
                last_error = e
        raise PublishApiError(f"No se pudo subir {rel_path} tras {UPLOAD_ATTEMPTS} intentos: {last_error}")

    def publish(self, session_id, manifest, delete, extra_files):
        return self._request(
            "POST",
            f"/sessions/{session_id}/publish",
            json={"manifest": manifest, "delete": delete, "extraFiles": extra_files},
            timeout=PUBLISH_TIMEOUT,
        )
