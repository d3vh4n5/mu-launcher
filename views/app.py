from tkinter import Tk, Label, Frame
import tkinter
import customtkinter as ctk
from components.frame_lang import load_frame_lang
from components.frame_window import load_frame_window
from components.frame_audio import load_frame_audio
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
from const.config import app_width,app_heigh, VERSION
from const.texts import TEXTS

class App():
    def __init__(self):
        # =========================
        # UI
        # =========================
        ctk.set_appearance_mode("dark")
        ctk.set_widget_scaling(1.0)  # Los widgets no se agrandan por el zoom de Windows
        ctk.set_window_scaling(1.0)  # La ventana mantiene su tamaño exacto en píxeles
        root = ctk.CTk()
        #root.overrideredirect(True) #Elimina la barra de ventana
        root.title("Mu Launcher - Hanster")

        x = root.winfo_screenmmwidth() *  2
        y = int(root.winfo_screenheight() * 0.3)
        root.geometry(f"{app_width}x{app_heigh}+"+ str(x) + '+' + str(y))
        root.resizable(False, False)
        
        img_icon_data = base64.b64decode(ICONO_BASE64)
        with open("temp_icon.ico", "wb") as tmp:
            tmp.write(img_icon_data)
        root.iconbitmap("temp_icon.ico")
        os.remove("temp_icon.ico")
        style(root)
        root.config(bg=bg_color)
        root.attributes("-alpha", 0.9)

        # --- Cargar y usar un logo (ejemplo) ---
        # Puedes ajustar el tamaño o no pasarlo si quieres el tamaño original
        logo_mu_image_tk = get_image_from_base64(HERO, size=(app_width, 150))
        logo_label = Label(root, image=logo_mu_image_tk, bd=0) # bd=0 para que no tenga borde
        logo_label.pack(pady=0) # Ejemplo de posicionamiento

        
        # Titulo
        Label(
            root,
            text=PROJECT_NAME,
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg="white",
        ).pack(pady=10)

        # -------- FRAMES -----------------------------
        frame_window= Frame(root, width=app_width, bg=bg_color)
        frame_audio = Frame(root, width=app_width, bg="#0A0A0A", pady=10)
        frame_idioma = Frame(root, bg=bg_color)

        frames = []
        frames.append(frame_window)
        frames.append(frame_audio)
        frames.append(frame_idioma)

        for frame in frames:
            frame.pack(fill="x", pady=10)

        state = AppState()

        load_frame_window(frame_window, state)
        load_frame_audio(frame_audio, state)
        load_frame_lang(frame_idioma, state)

        # Botón jugar
        btn = ctk.CTkButton(
                root,
                text=TEXTS[state.lang.get()]["play"],
                width=250,
                anchor=tkinter.CENTER,
                fg_color=primary_color,
                command=lambda: launch_game(
                    # server_var.get(),
                    "Online",
                    state.window_mode.get(),
                    state.resolution.get(),
                    state.audio.get(),
                    state.music.get(),
                    state.volume.get(),
                    state.lang.get()
                ),
            )
        btn.pack(pady=(10, 0))

        # Enlace
        # label = Label(root, text=TEXTS[state.lang.get()]["register"], fg="dodger blue", cursor="hand2", font=("Arial", 10))
        # label.config(bg=bg_color, pady=10)
        # label.pack(pady=(10, 0))
        # label.bind("<Button-1>", abrir_enlace)

        version = Label(root, text=f"{TEXTS[state.lang.get()]["version"]}: {VERSION}", fg="white", font=("Courier New", 8))
        version.config(bg=bg_color, pady=10)
        version.pack(pady=(10, 0))
        #root.update() # Forzar a la ventana a existir internamente
        #pywinstyles.apply_style(root, "dark") # Aplica el estilo oscuro a la ventana (si es compatible)
        pywinstyles.change_header_color(root, "#000000")
        root.mainloop()

