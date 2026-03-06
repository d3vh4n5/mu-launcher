from tkinter import Tk, Label, Frame
import tkinter
import customtkinter as ctk
from components.frame_lang import load_frame_lang
from components.frame_update import load_frame_update
from components.frame_window import load_frame_window
from components.frame_audio import load_frame_audio
from components.frame_server import load_frame_server
from const.config import PROJECT_NAME
import base64
import os
from assets.icono_data import ICONO_BASE64
from assets.imagenes_launcher_data import HERO
from functions.functions import abrir_enlace, launch_game
from utils.image_converter import get_image_from_base64
import pywinstyles
from utils.state import AppState
from utils.styles import style
from const.colors import bg_color, primary_color
from const.config import app_width,app_heigh, VERSION, components_width
from const.texts import TEXTS

class Options():
    def __init__(self, state: AppState):
        print('resolucion actual: ' + state.resolution.get())
        print('sonido actual: ', state.audio.get())
        print('idioma actual: ' + state.lang.get())
        print('ventana actual: ', state.window_mode.get())
        print('volumen actual: ' + str(state.volume.get()))
        # =========================
        # UI
        # =========================
        ctk.set_appearance_mode("dark")
        ctk.set_widget_scaling(1.0)  # Los widgets no se agrandan por el zoom de Windows
        ctk.set_window_scaling(1.0)  # La ventana mantiene su tamaño exacto en píxeles
        root = ctk.CTk()
        #root.overrideredirect(True) #Elimina la barra de ventana
        root.title("Options")

        x = root.winfo_screenmmwidth() *  2
        y = int(root.winfo_screenheight() * 0.3)
        root.geometry(f"{app_width}x500+"+ str(x) + '+' + str(y))
        root.resizable(False, False)
        
        img_icon_data = base64.b64decode(ICONO_BASE64)
        with open("temp_icon.ico", "wb") as tmp:
            tmp.write(img_icon_data)
        root.iconbitmap("temp_icon.ico")
        os.remove("temp_icon.ico")
        style(root)
        root.config(bg=bg_color)
        root.attributes("-alpha", 0.9)
        
        # Titulo
        Label(
            root,
            text="Options",
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg="white",
        ).pack(pady=10)

     

        # -------- FRAMES -----------------------------
        frame_window= Frame(root, width=app_width, bg=bg_color)
        frame_audio = Frame(root, width=app_width, bg="#0A0A0A", pady=10)
        frame_idioma = Frame(root, bg=bg_color)
        frame_server = Frame(root, bg=bg_color)
        frame_update = Frame(root, bg=bg_color)

        frames = []
        frames.append(frame_window)
        frames.append(frame_audio)
        frames.append(frame_idioma)
        frames.append(frame_server)
        frames.append(frame_update)

        for frame in frames:
            frame.pack(fill="x", pady=10)


        load_frame_window(frame_window, state)
        load_frame_audio(frame_audio, state)
        load_frame_lang(frame_idioma, state)

        btn = ctk.CTkButton(
            root,
            text=f"Guardar",
            width=components_width,
            anchor=tkinter.CENTER,
            fg_color=primary_color,
            command=lambda: [state.save_all(), root.after(200, root.destroy)] # Guardar y cerrar ventana
        )
        btn.pack(pady=10)

        #root.update() # Forzar a la ventana a existir internamente
        #pywinstyles.apply_style(root, "dark") # Aplica el estilo oscuro a la ventana (si es compatible)
        pywinstyles.change_header_color(root, "#000000")
        root.mainloop()

