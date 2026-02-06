from tkinter import Tk, Label, Frame
from components.frame1 import load_frame1
from const.config import PROJECT_NAME
import base64
import os
from assets.icono_data import ICONO_BASE64
from assets.imagenes_launcher_data import HERO
from utils.image_converter import get_image_from_base64
import pywinstyles
from utils.styles import style
from const.colors import bg_color
from const.config import app_width

class App():
    def __init__(self):
        # =========================
        # UI
        # =========================
        root = Tk()
        #root.overrideredirect(True) #Elimina la barra de ventana
        root.title(PROJECT_NAME)
        x = root.winfo_screenmmwidth() *  2
        y = int(root.winfo_screenheight() * 0.3)
        root.geometry(f"{app_width}x650+"+ str(x) + '+' + str(y))
        root.resizable(False, False)
        img_icon_data = base64.b64decode(ICONO_BASE64)
        with open("temp_icon.ico", "wb") as tmp:
            tmp.write(img_icon_data)
        root.iconbitmap("temp_icon.ico")
        os.remove("temp_icon.ico")
        style(root)
        # --- Cargar y usar un logo (ejemplo) ---
        # Puedes ajustar el tamaño o no pasarlo si quieres el tamaño original
        logo_mu_image_tk = get_image_from_base64(HERO, size=(app_width, 150))
        logo_label = Label(root, image=logo_mu_image_tk, bd=0) # bd=0 para que no tenga borde
        logo_label.pack(pady=0) # Ejemplo de posicionamiento

        # -------- FRAMES -----------------------------

        

        frame1= Frame(root, width=app_width, height=500, bg=bg_color, pady=30)
        frame2= Frame(root, bg=bg_color)
        # frame1.pack()
        # frame1.grid(row=0, column=0)

        frames = []
        frames.append(frame1)
        #frames.append(frame2)

        # for frame in (frame1, frame2):
            # frame.grid(row=0, column=0)
        for frame in frames:
            frame.pack()
        
        load_frame1(frame1)

        root.update() # Forzar a la ventana a existir internamente
        #pywinstyles.apply_style(root, "dark")
        pywinstyles.change_header_color(root, "#000000")
        root.mainloop()

