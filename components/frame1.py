from tkinter import ttk, Checkbutton, BooleanVar, StringVar, Label, Button
from const.config import PROJECT_NAME, RESOLUTION_MAP, SERVER_FILES
from components.button import ButtonWithHover
from functions.functions import launch_game, get_registry_value

def load_frame1(frame1):
    frame1.pack_propagate(False)
    Label(
        frame1,
        text=PROJECT_NAME,
        font=("Arial", 14, "bold"),
        bg="black",
        fg="white",
    ).pack(pady=10)

    # Selector de servidor
    Label(
        frame1,
        bg="black",
        fg="white",
        text="Servidor"
    ).pack()
    server_var = StringVar(value="Online")

    server_combo = ttk.Combobox(
        frame1,
        textvariable=server_var,
        values=list(SERVER_FILES.keys()),
        state="readonly",
        width=40,
    )
    server_combo.pack(pady=5)
    server_combo.set("Online")
    server_combo.textvariable = server_var #Refuerzo el valor de la variable porque dentro de funciones se pierde

    

    # resolucion
    Label(
        frame1,
        text="Resolución",
        bg="black",
        fg="white",
    ).pack()

    resolution_var = StringVar(value="800 x 600")
    val_registro = get_registry_value("Resolution")
    
    if val_registro is not False:
        mapa_invertido = {v: k for k, v in RESOLUTION_MAP.items()}
        if val_registro in mapa_invertido:
            resolution_var.set(mapa_invertido[val_registro])

    resolution_combo = ttk.Combobox(
        frame1,
        textvariable=resolution_var,
        values=list(RESOLUTION_MAP.keys()),
        state="readonly",
        width=40
    )
    resolution_combo.pack(pady=5)
    resolution_combo.textvariable = resolution_var

    # Modo ventana
    window_var = BooleanVar(value=True)
    window_val = get_registry_value("WindowMode")

    if window_val is not False:
        window_var.set(True if window_val == 1 else False)
    else:
        window_var.set(True)

    check = Checkbutton(
        frame1,
        text="Modo ventana",
        variable=window_var,
        bg="black",           # Fondo normal
        fg="white",           # Color del texto
        selectcolor="black",  # <--- IMPORTANTE: Fondo de la cajita del tick
        activebackground="black", # Fondo cuando haces clic
        activeforeground="white", # Texto cuando haces clic
        highlightthickness=0,     # Quita el borde gris de enfoque
        bd=0                      # Quita bordes extra
    )
    check.pack(pady=10)
    check.variable = window_var

    server = server_var.get()
    windowed = window_var.get()
    resolution = resolution_var.get()

    # Botón jugar
    ButtonWithHover(frame1, "JUGAR", lambda: launch_game(server, windowed, resolution))