
from tkinter import Radiobutton
from utils.state import AppState


def load_frame_lang(frame_idioma, state: AppState):
    # Configuramos las 3 columnas para que tengan el mismo ancho
    frame_idioma.grid_columnconfigure(0, weight=1)
    frame_idioma.grid_columnconfigure(1, weight=1)
    frame_idioma.grid_columnconfigure(2, weight=1)

    lang_style = {
        "variable": state.lang,
        "bg": "black",
        "fg": "white",
        "selectcolor": "#009C34",
        "activebackground": "black",
        "activeforeground": "white",
        "highlightthickness": 0,
        "font": ("Arial", 10),
        "command": state.save_lang
    }

    # Radiobuttons
    Radiobutton(frame_idioma, text="Español", value="Spn", **lang_style).grid(row=0, column=0)
    Radiobutton(frame_idioma, text="English", value="Eng", **lang_style).grid(row=0, column=1)
    Radiobutton(frame_idioma, text="Português", value="Por", **lang_style).grid(row=0, column=2)