import os

from updater.process import force_close_launcher

def get_files_in_directory(directory):
    """Returns a list of files in the specified directory."""
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except FileNotFoundError:
        print(f"Directory '{directory}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred while accessing the directory: {e}")
        return []

def file_exists(file_path):
    """Checks if a file exists at the specified path."""
    return os.path.isfile(file_path)

# --- Lógica de reemplazo ---
def update_executable(old_path, new_path):
    try:
        # Convertimos a objeto Path si no lo son (por seguridad)
        import pathlib
        old_path = pathlib.Path(old_path)
        new_path = pathlib.Path(new_path)

        # 1. Crear la ruta del backup: launcher.exe -> launcher.exe.bak
        temp_old = old_path.with_suffix(old_path.suffix + ".bak")
        
        # 2. Renombrar el viejo a .bak
        if old_path.exists():
            if temp_old.exists():
                temp_old.unlink() # Esto es como os.remove() en pathlib
            old_path.rename(temp_old)
        
        # 3. Mover el nuevo al lugar del original
        new_path.rename(old_path)
        
        print("Actualización exitosa.")
        return True
    except Exception as e:
        print(f"Error al reemplazar: {e}")
        return False
