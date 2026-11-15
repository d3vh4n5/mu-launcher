"""
Evita que el launcher se cuelgue al arrancar cuando WMI de Windows no responde.

Desde Python 3.12, platform.win32_ver()/platform.release() consultan WMI
(Win32_OperatingSystem). Si el servicio WMI de la PC está trabado, esa consulta
no devuelve nunca y el proceso queda colgado sin ventana. customtkinter importa
darkdetect, que llama a platform.release() al importarse, así que el cuelgue
ocurre antes de que se escriba cualquier log.

Deshabilitando el módulo _wmi, platform usa sys.getwindowsversion() y el
registro, que dan la misma información sin depender de WMI.

Importar este módulo ANTES que customtkinter / darkdetect.
"""
import platform

if hasattr(platform, "_wmi"):
    platform._wmi = None
