import requests
from const.config import API_URL
import time

class ServerService:
    def __init__(self):
        self.base_url = API_URL

    def fetch_servers(self):
        #time.sleep(2)  # Simula un retraso de red
        try:
            response = requests.get(API_URL + "/api/launcher/servers")
            response.raise_for_status()
            
            servers = response.json()
            return servers
        except Exception as e:
            print("Error al obtener servidores:", e)
            return []
    
    @staticmethod
    def download_and_replace_config(base_url, file_path_api, local_filename="ServerInfo.sse"):
        """
        Descarga el archivo desde la API y pisa el archivo local.
        base_url: ej. "http://localhost:3000"
        file_path_api: ej. "/downloads/Mu99bClassic/ServerInfo.sse"
        """
        url = f"{base_url}{file_path_api}"
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status() # Lanza error si hay 404 o 500
            
            # Escribir el archivo (esto pisa el anterior automáticamente)
            with open(local_filename, "wb") as f:
                f.write(response.content)
            
            print(f"Archivo {local_filename} actualizado con éxito.")
            return True
        except Exception as e:
            print(f"Error al descargar configuración: {e}")
            raise e # Re-lanzamos para que la UI sepa que falló