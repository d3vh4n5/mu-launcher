from tkinter import StringVar, Label
from customtkinter import CTkComboBox, CTkProgressBar
from const.colors import *
from const.config import API_URL, components_width
from const.texts import TEXTS
from utils.state import AppState
from services.api_service import ServerService
import threading

def load_frame_server(frame1, state: AppState, btn):
    # 1. Definimos la etiqueta y la variable
    # Label(
    #     frame1,
    #     bg="black",
    #     fg="white",
    #     text="Servidor"
    # ).pack()
    
    server_var = StringVar(value="Obteniendo servidores...")

    # 2. Creamos el ComboBox (inicialmente deshabilitado para evitar clics vacíos)
    server_combo = CTkComboBox(
        frame1,
        variable=server_var,
        values=["Cargando..."],
        state="disabled", # Lo bloqueamos hasta tener datos
        width=components_width,
        border_color=primary_color,
        button_color=primary_color,
        command=lambda choice: on_server_selected(choice)
    )
    server_combo.pack(pady=5)

    # Barra de progreso (inicialmente oculta o en 0)
    progress_bar = CTkProgressBar(
        frame1, 
        width=components_width, 
        progress_color=primary_color,
        mode="determinate" # O "indeterminate" si no sabemos el tamaño
    )
    progress_bar.set(0) # Empezar en 0
    progress_bar.pack(pady=10)
    progress_bar.pack_forget() # La ocultamos hasta que se necesite

    # 3. Función interna que el hilo ejecutará
    def async_load():
        service = ServerService()
        servers = service.fetch_servers() # Esto corre en segundo plano
        
        # 4. Usamos .after() para inyectar los datos en el hilo de la UI
        frame1.after(0, update_ui, servers)

    # 5. Función para actualizar los widgets una vez recibida la info
    def update_ui(servers):
        try:
            if servers:
                # Si 'servers' es una lista de diccionarios, extrae el nombre
                names = [s['name'] for s in servers] 
                server_combo.configure(values=names, state="readonly")
                server_combo.set(names[0])
                # Guardamos la lista completa en el estado global por si necesitas los IDs luego
                state.available_servers = servers
                state.set_can_launch(True)  # Ahora que tenemos servidores, permitimos lanzar el juego
                btn.configure(state="normal")
            else:
                raise Exception("No se recibieron servidores válidos")
        except Exception as e:
            print("Error al actualizar UI de servidores:", e)
            server_combo.configure(
                values=["Error de conexión"],
                state="disabled",
                border_color="red",
                button_color="red",
            )
            server_var.set("Error inesperado")
    
    def on_server_selected(choice):
        current_server = next((s for s in state.available_servers if s['name'] == choice), None)
        if not current_server: return

        # 1. Mostrar barra y deshabilitar botón mientras descarga
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        btn.configure(state="disabled", text="Actualizando...")

        def download_task():
            try:
                # Simulación de progreso (opcional, para archivos pequeños como este)
                # Para 500kb es casi instantáneo, pero así le das feedback al usuario
                for i in range(1, 11):
                    frame1.after(0, lambda v=i/10: progress_bar.set(v))
                    import time; time.sleep(0.05) 

                # La descarga real
                ServerService.download_and_replace_config(
                    API_URL,
                    current_server['fileUrl']
                )

                # 2. Éxito: Volvemos a habilitar todo
                frame1.after(0, lambda: finalize_download("Jugar", "normal", primary_color))
            except Exception as e:
                print(f"Error: {e}")
                frame1.after(0, lambda: finalize_download("Reintentar", "disabled", "red"))

        def finalize_download(btn_text, btn_state, btn_color=primary_color):
            btn.configure(text=btn_text, state=btn_state, fg_color=btn_color)
            progress_bar.pack_forget() # Ocultamos la barra al terminar

        # 3. LANZAR EN HILO (Vital para no congelar la UI)
        threading.Thread(target=download_task, daemon=True).start()

    # 6. Lanzamos el hilo
    threading.Thread(target=async_load, daemon=True).start()