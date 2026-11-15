import os
import sys
import json
import hashlib

# =========================
# CONFIGURACIÓN
# =========================

# Carpeta raíz del cliente: se puede pasar como argumento.
# Por defecto: <Mu Campana>/Client (relativo a este script, no al cwd).
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(
    os.path.join(_SCRIPT_DIR, "..", "..", "..", "Client")
)
OUTPUT_MANIFEST = os.path.join(_SCRIPT_DIR, "manifest.json")

if not os.path.isdir(CLIENT_DIR):
    sys.exit(f"No existe la carpeta del cliente: {CLIENT_DIR}")

# Se comparan en minúsculas (en Windows "temp" y "Temp" son la misma carpeta).
# Ojo: NO excluir "launcher", porque Data/Launcher (updater.exe, serverinfo/) se distribuye.
# Lo que genera el launcher en runtime (temp, logs) va a %LOCALAPPDATA%/MuCampana.
EXCLUDE_DIRS = {
    "logs",
    "screenshots",
    "temp",        # restos viejos: Data/temp/new_launcher.exe
    ".git",
    "__pycache__"
}

EXCLUDE_FILES = {
    "manifest.json",
    "manifest.py",
    "muerror.dmp",
    "launcher.exe",   # se actualiza por su propio flujo (API + updater), no por manifest
    "tool.exe",
}

EXCLUDE_EXTENSIONS = {".log", ".dmp"}

# Rutas relativas exactas (minúsculas, con "/") a excluir.
# updater.exe en la raíz es la ubicación vieja: ahora va en Data/Launcher/updater.exe
EXCLUDE_PATHS = {
    "updater.exe",
}

MANIFEST_VERSION = "1.0.0"


# =========================
# FUNCIONES
# =========================

def calcular_sha256(path):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(8192), b""):
            sha256.update(bloque)
    return sha256.hexdigest()


# =========================
# GENERADOR DE MANIFEST
# =========================

files_manifest = []

for root, dirs, files in os.walk(CLIENT_DIR):
    # 🔴 excluir directorios
    dirs[:] = [d for d in dirs if d.lower() not in EXCLUDE_DIRS]

    for file in files:
        if file.lower() in EXCLUDE_FILES:
            continue
        if os.path.splitext(file)[1].lower() in EXCLUDE_EXTENSIONS:
            continue

        full_path = os.path.join(root, file)

        # path relativo (para que coincida en el launcher)
        relative_path = os.path.relpath(full_path, CLIENT_DIR).replace("\\", "/")
        if relative_path.lower() in EXCLUDE_PATHS:
            continue

        size = os.path.getsize(full_path)
        sha256 = calcular_sha256(full_path)

        files_manifest.append({
            "path": relative_path,
            "size": size,
            "sha256": sha256
        })

if not files_manifest:
    sys.exit(f"No se encontraron archivos en {CLIENT_DIR}; no se escribe un manifest vacío.")

manifest = {
    "version": MANIFEST_VERSION,
    "file_count": len(files_manifest),
    "files": files_manifest
}

with open(OUTPUT_MANIFEST, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"✅ Manifest generado correctamente: {OUTPUT_MANIFEST}")
print(f"📦 Archivos incluidos: {len(files_manifest)}")
