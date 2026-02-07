from tkinter import HORIZONTAL, Frame, Scale, ttk, Checkbutton, BooleanVar, StringVar, Label, IntVar, Radiobutton
from const.colors import *
from const.config import PROJECT_NAME, RESOLUTION_MAP
from functions.functions import get_registry_value, abrir_enlace, set_reg_dword
from utils.state import AppState

def load_frame_window(frame1, state: AppState):
    #frame1.pack_propagate(False)

    # # Selector de servidor
    # Label(
    #     frame1,
    #     bg="black",
    #     fg="white",
    #     text="Servidor"
    # ).pack()
    # server_var = StringVar(value="Online")

    # server_combo = ttk.Combobox(
    #     frame1,
    #     textvariable=server_var,
    #     values=list(SERVER_FILES.keys()),
    #     state="readonly",
    #     width=40,
    # )
    # server_combo.pack(pady=5)
    # server_combo.set("Online")
    # server_combo.textvariable = server_var #Refuerzo el valor de la variable porque dentro de funciones se pierde

    

    # resolucion
    Label(
        frame1,
        text="Resolución",
        bg="black",
        fg="white",
    ).pack()

    resolution_combo = ttk.Combobox(
        frame1,
        textvariable=state.resolution,
        values=list(RESOLUTION_MAP.keys()),
        state="readonly",
        width=44
    )
    resolution_combo.pack(pady=5)
    resolution_combo.textvariable = state.resolution
    resolution_combo.bind(
        "<<ComboboxSelected>>",
        state.save_resolution
    )

    # Modo ventana

    check = Checkbutton(
        frame1,
        text="Modo ventana",
        variable=state.window_mode,
        bg="black",           # Fondo normal
        fg="white",           # Color del texto
        selectcolor="black",  # <--- IMPORTANTE: Fondo de la cajita del tick
        activebackground="black", # Fondo cuando haces clic
        activeforeground="white", # Texto cuando haces clic
        highlightthickness=0,     # Quita el borde gris de enfoque
        bd=0,                      # Quita bordes extra
        command=state.save_window_mode
    )
    check.pack(pady=10)
    check.variable = state.window_mode
