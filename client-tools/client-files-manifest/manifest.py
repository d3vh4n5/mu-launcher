import os
import sys
import json

# Las exclusiones y el escaneo viven en client-tools/client_scan.py (compartido
# con tool.py, incluida la pestaña "Publicar en servidor").
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_SCRIPT_DIR))

from client_scan import (  # noqa: E402
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_EXCLUDE_FILES,
    build_manifest,
    scan_client,
)

# =========================
# CONFIGURACIÓN
# =========================

# Carpeta raíz del cliente: se puede pasar como argumento.
# Por defecto: <Mu Campana>/Client (relativo a este script, no al cwd).
CLIENT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(
    os.path.join(_SCRIPT_DIR, "..", "..", "..", "Client")
)
OUTPUT_MANIFEST = os.path.join(_SCRIPT_DIR, "manifest.json")
MANIFEST_VERSION = "1.0.0"

if not os.path.isdir(CLIENT_DIR):
    sys.exit(f"No existe la carpeta del cliente: {CLIENT_DIR}")

files_manifest = scan_client(CLIENT_DIR, DEFAULT_EXCLUDE_DIRS, DEFAULT_EXCLUDE_FILES)

if not files_manifest:
    sys.exit(f"No se encontraron archivos en {CLIENT_DIR}; no se escribe un manifest vacío.")

with open(OUTPUT_MANIFEST, "w", encoding="utf-8") as f:
    json.dump(build_manifest(files_manifest, MANIFEST_VERSION), f, indent=2)

print(f"Manifest generado correctamente: {OUTPUT_MANIFEST}")
print(f"Archivos incluidos: {len(files_manifest)}")
