"""Escaneo de la carpeta del cliente, compartido por el generador de manifest
(tool.py y manifest.py) y la publicación al servidor.

Todas las comparaciones de rutas son sin distinguir mayúsculas: en Windows
"Data/X.bmd" y "data/x.bmd" son el mismo archivo.
"""
import hashlib
import os

# Ojo: NO excluir "launcher": Data/Launcher (updater.exe, serverinfo/) se distribuye.
DEFAULT_EXCLUDE_DIRS = {"logs", "screenshots", "temp", ".git", "__pycache__"}

DEFAULT_EXCLUDE_FILES = {
    "manifest.json",
    "manifest.py",
    "tool.py",
    "tool.exe",
    "muerror.dmp",
    # Se actualiza por su propio flujo (API + updater), no por manifest
    "launcher.exe",
}

EXCLUDE_EXTENSIONS = {".log", ".dmp"}

# Rutas relativas exactas. updater.exe en la raíz es la ubicación vieja
# (ahora va en Data/Launcher/updater.exe).
EXCLUDE_PATHS = {"updater.exe"}

LAUNCHER_EXE = "launcher.exe"


def sha256_file(path):
    sha = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def _lower(names):
    return {name.casefold() for name in names}


def is_excluded(rel_path, exclude_dirs, exclude_files):
    """rel_path con "/". Las exclusiones se comparan en minúsculas."""
    parts = rel_path.casefold().split("/")
    name = parts[-1]
    return (
        any(part in _lower(exclude_dirs) for part in parts[:-1])
        or name in _lower(exclude_files)
        or os.path.splitext(name)[1] in EXCLUDE_EXTENSIONS
        or rel_path.casefold() in EXCLUDE_PATHS
    )


def scan_client(client_dir, exclude_dirs, exclude_files, on_progress=None):
    """[{"path", "size", "sha256"}] ordenado por path, con "/"."""
    exclude_dirs = _lower(exclude_dirs)
    rel_paths = []
    for root, dirs, files in os.walk(client_dir):
        dirs[:] = [d for d in dirs if d.casefold() not in exclude_dirs]
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), client_dir).replace("\\", "/")
            if not is_excluded(rel, exclude_dirs, exclude_files):
                rel_paths.append(rel)

    rel_paths.sort()
    total = len(rel_paths)
    result = []
    for i, rel in enumerate(rel_paths):
        full = os.path.join(client_dir, *rel.split("/"))
        result.append({"path": rel, "size": os.path.getsize(full), "sha256": sha256_file(full)})
        if on_progress:
            on_progress(i + 1, total, rel)
    return result


def build_manifest(files, version):
    return {"version": version, "file_count": len(files), "files": files}


def diff_plan(local, remote, mirror, exclude_dirs, exclude_files):
    """Qué hay que subir y borrar para que el servidor quede como la carpeta local.

    delete solo en modo espejo, y nunca launcher.exe ni lo excluido.
    """
    remote_by_key = {item["path"].casefold(): item for item in remote}
    local_keys = set()
    new, modified, unchanged = [], [], 0

    for item in local:
        key = item["path"].casefold()
        local_keys.add(key)
        other = remote_by_key.get(key)
        if other is None:
            new.append(item["path"])
        elif other["sha256"].casefold() != item["sha256"].casefold():
            modified.append(item["path"])
        else:
            unchanged += 1

    delete = []
    if mirror:
        for key, item in remote_by_key.items():
            if key in local_keys or key == LAUNCHER_EXE:
                continue
            if is_excluded(item["path"], exclude_dirs, exclude_files):
                continue
            delete.append(item["path"])

    return {"new": new, "modified": modified, "delete": sorted(delete), "unchanged": unchanged}


def looks_like_client(client_dir):
    """Evita publicar (y en espejo, borrar todo) desde una carpeta equivocada."""
    return os.path.isfile(os.path.join(client_dir, "main.exe"))
