from tkinter import HORIZONTAL, Label, Scale, Checkbutton
from const.texts import TEXTS
from utils.state import AppState

def load_frame_audio(frame_audio, state: AppState):
    frame_audio.pack_propagate(False)
    frame_audio.grid_columnconfigure(0, weight=1)
    frame_audio.grid_columnconfigure(1, weight=1)

    ### Audio On/Off
    audio_check = Checkbutton(
        frame_audio,
        text=TEXTS[state.lang.get()]["audio"],
        variable=state.audio,
        bg="black",           # Fondo normal
        fg="white",           # Color del texto
        selectcolor="black",  # <--- IMPORTANTE: Fondo de la cajita del tick
        activebackground="black", # Fondo cuando haces clic
        activeforeground="white", # Texto cuando haces clic
        highlightthickness=0,     # Quita el borde gris de enfoque
        bd=0,                      # Quita bordes extra
        command=state.save_audio
    )
    audio_check.grid(row=0, column=0, sticky='e', padx=10, pady=20)
    audio_check.variable = state.audio

     ### Music On/Off

    music_check = Checkbutton(
        frame_audio,
        text=TEXTS[state.lang.get()]["music"],
        variable=state.music,
        bg="black",           # Fondo normal
        fg="white",           # Color del texto
        selectcolor="black",  # <--- IMPORTANTE: Fondo de la cajita del tick
        activebackground="black", # Fondo cuando haces clic
        activeforeground="white", # Texto cuando haces clic
        highlightthickness=0,     # Quita el borde gris de enfoque
        bd=0,                      # Quita bordes extra
        command=state.save_music
    )
    music_check.grid(row=0, column=1, sticky='w', padx=10, pady=20)
    music_check.variable = state.music

    # Fila 1: Etiqueta de volumen
    Label(frame_audio, text=TEXTS[state.lang.get()]["volume"], bg="black", fg="white", font=("Arial", 8)).grid(row=1, column=0, columnspan=2)

    # Fila 2: La barra
    volume_scale = Scale(
        frame_audio, from_=0, to=10, orient=HORIZONTAL, 
        variable=state.volume, bg="black", fg="white", 
        troughcolor="#1a1a1a", highlightthickness=0,
        bd=0, length=200,
        command=lambda v: state.save_volume(int(v))
    )
    volume_scale.grid(row=2, column=0, columnspan=2, sticky='n')