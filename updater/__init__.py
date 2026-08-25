import os
import sys
import subprocess
from pathlib import Path

from utils.logger import logger

def trigger_launcher_update(new_exe_path, target_exe_path=None, updater_exe_path=None):
    """
    Inicia el proceso del updater de forma independiente pasando las rutas y el PID actual,
    y luego finaliza el launcher actual para permitir el reemplazo del ejecutable.
    """
    base_dir = Path.cwd()
    if target_exe_path is None:
        if getattr(sys, 'frozen', False):
            target_exe_path = Path(sys.executable)
        else:
            target_exe_path = base_dir / "launcher.exe"

    pid = os.getpid()
    new_exe_str = str(new_exe_path)
    target_exe_str = str(target_exe_path)

    if getattr(sys, 'frozen', False):
        updater_exe = Path(updater_exe_path) if updater_exe_path else base_dir / "updater.exe"
        logger.info(f"Preparando ejecución del updater: ruta={updater_exe.resolve()}, existe={updater_exe.exists()}")
        if updater_exe.exists():
            cmd = [str(updater_exe), "--new-exe", new_exe_str, "--target-exe", target_exe_str, "--pid", str(pid)]
        else:
            logger.warning("updater.exe no existe; se utilizará el módulo updater.updater como fallback.")
            cmd = [sys.executable, "-m", "updater.updater", "--new-exe", new_exe_str, "--target-exe", target_exe_str, "--pid", str(pid)]
    else:
        cmd = [sys.executable, "-m", "updater.updater", "--new-exe", new_exe_str, "--target-exe", target_exe_str, "--pid", str(pid)]

    logger.info(f"Ejecutando updater con comando: {cmd}")
    subprocess.Popen(cmd, cwd=str(base_dir))
    sys.exit(0)
