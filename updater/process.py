# Chequear un proceso o tarea activo

import psutil
import time

# all_processes = psutil.process_iter(['pid', 'name', 'username'])

# for proc in all_processes:
#     if proc.info['name'] == 'launcher.exe':
#         print(proc.info)
#         psutil.Process(proc.info['pid']).kill()

def process_exists(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

def process_kill(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            proc.kill()

def process_find_and_kill(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            proc.kill()
            return True
    return False

def force_close_launcher(process_name, timeout=5):
    """
    Busca, termina y espera a que el sistema libere el archivo.
    """
    targets = [p for p in psutil.process_iter(['name']) 
               if p.info['name'].lower() == process_name.lower()]
    
    if not targets:
        return True # No hay nada que cerrar, podemos proceder

    for p in targets:
        try:
            print(f"Terminando proceso {p.pid} ({p.info['name']})...")
            p.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Esperamos a que el SO confirme que ya no existen
    gone, alive = psutil.wait_procs(targets, timeout=timeout)
    
    for p in alive:
        try:
            p.kill() # Si no cerró por las buenas, va por las malas
        except:
            pass
            
    # Un pequeño truco: verificar si el archivo sigue bloqueado por el SO
    time.sleep(0.5) 
    return True



if __name__ == "__main__":
    if process_exists('launcher.exe'):
        print("El proceso está en ejecución.")
        force_close_launcher('launcher.exe')
    else:
        print("El proceso no está en ejecución.")