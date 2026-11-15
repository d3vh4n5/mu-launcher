"""
Compila launcher.exe, updater.exe y tool.exe.

La versión sale SOLO de VERSION en const/config.py: este script la escribe en
file_version_info.txt (metadatos del exe), y la API la lee del launcher.exe
publicado para decidir si los jugadores tienen que actualizar.

Uso (desde la carpeta Launcher):
    .venv\\Scripts\\python build.py              # compila los 3
    .venv\\Scripts\\python build.py launcher     # solo algunos
    .venv\\Scripts\\python build.py --copy       # además copia a ../Client
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLIENT_DIR = ROOT.parent / "Client"
TARGETS = {
    "launcher": ("launcher.spec", CLIENT_DIR / "launcher.exe"),
    "updater": ("updater.spec", CLIENT_DIR / "Data" / "Launcher" / "updater.exe"),
    "tool": ("tool.spec", None),  # herramienta de admin: no va al cliente
}


def read_version() -> str:
    text = (ROOT / "const" / "config.py").read_text(encoding="utf-8")
    m = re.search(r'^VERSION\s*=\s*["\'](\d+)\.(\d+)\.(\d+)["\']', text, re.M)
    if not m:
        sys.exit("No se encontró VERSION=\"x.y.z\" en const/config.py")
    return ".".join(m.groups())


def write_version_info(version: str):
    path = ROOT / "file_version_info.txt"
    with open(path, encoding="utf-8", newline="") as f:  # conserva CRLF
        text = f.read()
    nums = ", ".join(version.split(".") + ["0"])
    text = re.sub(r"filevers=\([^)]*\)", f"filevers=({nums})", text)
    text = re.sub(r"prodvers=\([^)]*\)", f"prodvers=({nums})", text)
    text = re.sub(r"(StringStruct\(u'(?:FileVersion|ProductVersion)', u')[^']*'",
                  rf"\g<1>{version}'", text)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    copy = "--copy" in sys.argv
    names = args or list(TARGETS)
    unknown = set(names) - set(TARGETS)
    if unknown:
        sys.exit(f"Desconocido: {', '.join(unknown)}. Opciones: {', '.join(TARGETS)}")

    version = read_version()
    write_version_info(version)
    print(f"Versión {version} -> file_version_info.txt")

    if "launcher" in names and not (ROOT / ".env").exists():
        sys.exit("Falta Launcher/.env (se embebe en launcher.exe con API_URL/API_KEY)")

    for name in names:
        spec, dest = TARGETS[name]
        print(f"\n=== Compilando {name} ({spec})")
        subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--noconfirm", spec],
            cwd=ROOT, check=True,
        )
        if copy and dest:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "dist" / f"{name}.exe", dest)
            print(f"Copiado a {dest}")

    print(f"\nListo: versión {version}")


if __name__ == "__main__":
    main()
