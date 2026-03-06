import requests
from const.config import API_URL, API_KEY
import time

class ServerService:
    def __init__(self):
        self.base_url = API_URL
        self.headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }

    def fetch_servers(self):

        try:
            response = requests.get(
                f"{API_URL}/api/launcher/servers", 
                headers=self.headers, 
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print("Error al obtener servidores:", e)
            return []
    
    def download_and_replace_config(self, base_url, file_path_api, local_filename="ServerInfo.sse"):
        """
        Descarga el archivo desde la API y pisa el archivo local.
        base_url: ej. "http://localhost:3000"
        file_path_api: ej. "/downloads/Mu99bClassic/ServerInfo.sse"
        """
        print(f"Descargando configuración desde {base_url}{file_path_api}...")
        url = f"{base_url}{file_path_api}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status() # Lanza error si hay 404 o 500
            
            # Escribir el archivo (esto pisa el anterior automáticamente)
            with open(local_filename, "wb") as f:
                f.write(response.content)
            
            print(f"Archivo {local_filename} actualizado con éxito.")
            return True
        except Exception as e:
            print(f"Error al descargar configuración: {e}")
            raise e # Re-lanzamos para que la UI sepa que falló