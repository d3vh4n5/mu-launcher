import os
import psutil
import time

def process_exists(process_name):
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'].lower() == process_name.lower() and proc.info['pid'] != os.getpid():
            return True
    return False

def process_kill(process_name):
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'].lower() == process_name.lower() and proc.info['pid'] != os.getpid():
            try:
                proc.kill()
            except Exception:
                pass

def force_close_launcher(process_name, timeout=5):
    """
    Busca, termina y espera a que el sistema libere el archivo.
    """
    targets = [p for p in psutil.process_iter(['name', 'pid']) 
               if p.info['name'].lower() == process_name.lower() and p.info['pid'] != os.getpid()]
    
    if not targets:
        return True

    for p in targets:
        try:
            p.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    gone, alive = psutil.wait_procs(targets, timeout=timeout)
    
    for p in alive:
        try:
            p.kill()
        except Exception:
            pass
            
    time.sleep(0.5) 
    return True