import os
import json
import hashlib

# =========================
# CONFIGURACIÓN
# =========================

CLIENT_DIR = r"./build"   # carpeta raíz del cliente
OUTPUT_MANIFEST = "manifest.json"

EXCLUDE_DIRS = {
    "Logs",
    "Screenshots",
    "Temp",
    "Launcher",
    ".git",
    "__pycache__"
}

EXCLUDE_FILES = {
    "manifest.json"
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
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for file in files:
        if file in EXCLUDE_FILES:
            continue

        full_path = os.path.join(root, file)

        # path relativo (para que coincida en el launcher)
        relative_path = os.path.relpath(full_path, CLIENT_DIR).replace("\\", "/")

        size = os.path.getsize(full_path)
        sha256 = calcular_sha256(full_path)

        files_manifest.append({
            "path": relative_path,
            "size": size,
            "sha256": sha256
        })

manifest = {
    "version": MANIFEST_VERSION,
    "file_count": len(files_manifest),
    "files": files_manifest
}

with open(OUTPUT_MANIFEST, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"✅ Manifest generado correctamente: {OUTPUT_MANIFEST}")
print(f"📦 Archivos incluidos: {len(files_manifest)}")
