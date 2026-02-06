from tkinter import HORIZONTAL, Frame, Scale, ttk, Checkbutton, BooleanVar, StringVar, Label, IntVar, Radiobutton
from const.colors import *
from const.config import PROJECT_NAME, RESOLUTION_MAP, SERVER_FILES, app_width
from components.button import ButtonWithHover
from functions.functions import launch_game, get_registry_value, abrir_enlace, set_reg_dword

def load_frame1(frame1):
    frame1.pack_propagate(False)
    Label(
        frame1,
        text=PROJECT_NAME,
        font=("Arial", 14, "bold"),
        bg="black",
        fg="white",
    ).pack(pady=10)

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
        width=44
    )
    resolution_combo.pack(pady=5)
    resolution_combo.textvariable = resolution_var
    resolution_combo.bind(
        "<<ComboboxSelected>>",
        lambda e: set_reg_dword("Resolution", RESOLUTION_MAP[resolution_var.get()])
    )

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
        bd=0,                      # Quita bordes extra
        command=lambda: set_reg_dword("WindowMode", 1 if window_var.get() else 0)
    )
    check.pack(pady=10)
    check.variable = window_var

    frame_audio = Frame(frame1, width=app_width, height=200, bg="#0C0C0C")
    frame_audio.pack(pady=20, fill="x")
    frame_audio.pack_propagate(False)
    frame_audio.grid_columnconfigure(0, weight=1)
    frame_audio.grid_columnconfigure(1, weight=1)

    ### Audio On/Off
    audio_var = BooleanVar(value=True)
    audio_val = get_registry_value("SoundOnOff")

    if audio_val is not False:
        audio_var.set(True if audio_val == 1 else False)
    else:
        audio_var.set(True)

    audio_check = Checkbutton(
        frame_audio,
        text="Audio",
        variable=audio_var,
        bg="black",           # Fondo normal
        fg="white",           # Color del texto
        selectcolor="black",  # <--- IMPORTANTE: Fondo de la cajita del tick
        activebackground="black", # Fondo cuando haces clic
        activeforeground="white", # Texto cuando haces clic
        highlightthickness=0,     # Quita el borde gris de enfoque
        bd=0,                      # Quita bordes extra
        command=lambda: set_reg_dword("SoundOnOff", 1 if audio_var.get() else 0)
    )
    audio_check.grid(row=0, column=0, sticky='e', padx=10, pady=20)
    audio_check.variable = audio_var

     ### Music On/Off
    music_var = BooleanVar(value=True)
    music_val = get_registry_value("MusicOnOff")

    if music_val is not False:
        music_var.set(True if music_val == 1 else False)
    else:
        music_var.set(True)

    music_check = Checkbutton(
        frame_audio,
        text="Music",
        variable=music_var,
        bg="black",           # Fondo normal
        fg="white",           # Color del texto
        selectcolor="black",  # <--- IMPORTANTE: Fondo de la cajita del tick
        activebackground="black", # Fondo cuando haces clic
        activeforeground="white", # Texto cuando haces clic
        highlightthickness=0,     # Quita el borde gris de enfoque
        bd=0,                      # Quita bordes extra
        command=lambda: set_reg_dword("MusicOnOff", 1 if music_var.get() else 0)
    )
    music_check.grid(row=0, column=1, sticky='w', padx=10, pady=20)
    music_check.variable = music_var

    # Variable para el volumen (0 a 10)
    volume_var = IntVar(value=get_registry_value("VolumeLevel") or 5)

    # Fila 1: Etiqueta de volumen
    Label(frame_audio, text="Volumen", bg="black", fg="white", font=("Arial", 8)).grid(row=1, column=0, columnspan=2)

    # Fila 2: La barra
    volume_scale = Scale(
        frame_audio, from_=0, to=10, orient=HORIZONTAL, 
        variable=volume_var, bg="black", fg="white", 
        troughcolor="#1a1a1a", highlightthickness=0,
        bd=0, length=200,
        command=lambda v: set_reg_dword("VolumeLevel", int(v))
    )
    volume_scale.grid(row=2, column=0, columnspan=2, sticky='n')

    # Frame para Idiomas (dentro de frame1)
    frame_idioma = Frame(frame1, bg="black")
    frame_idioma.pack(pady=(10, 30), fill='x')
    
    # Configuramos las 3 columnas para que tengan el mismo ancho
    frame_idioma.grid_columnconfigure(0, weight=1)
    frame_idioma.grid_columnconfigure(1, weight=1)
    frame_idioma.grid_columnconfigure(2, weight=1)

    # Obtener valor y asegurar que sea un string válido
    val_reg = get_registry_value("LangSelection")
    lang_default = val_reg if val_reg in ["Spn", "Eng", "Por"] else "Spn"

    lang_var = StringVar(value=lang_default)
    frame_idioma.lang_var = lang_var # Evita que Python limpie la variable de la memoria

    lang_style = {
        "variable": lang_var,
        "bg": "black",
        "fg": "white",
        "selectcolor": "#009C34",
        "activebackground": "black",
        "activeforeground": "white",
        "highlightthickness": 0,
        "font": ("Arial", 10),
        "command": lambda: set_reg_dword("LangSelection", lang_var.get(), "REG_SZ")
    }

    # Radiobuttons
    Radiobutton(frame_idioma, text="Español", value="Spn", **lang_style).grid(row=0, column=0)
    Radiobutton(frame_idioma, text="English", value="Eng", **lang_style).grid(row=0, column=1)
    Radiobutton(frame_idioma, text="Português", value="Por", **lang_style).grid(row=0, column=2)

    # Botón jugar
    ButtonWithHover(
        frame1, 
        "JUGAR", 
        lambda: launch_game(
            # server_var.get(),
            "Online",
            window_var.get(),
            resolution_var.get(),
            audio_var.get(),
            music_var.get(),
            volume_var.get(),
            lang_var.get()
        )
    )

    # Enlace
    label = Label(frame1, text="Registrarse", fg="dodger blue", cursor="hand2", font=("Arial", 10))
    label.config(bg=bg_color, pady=30)
    label.pack(pady=(20, 0))
    label.bind("<Button-1>", abrir_enlace)