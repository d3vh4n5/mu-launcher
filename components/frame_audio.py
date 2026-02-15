import customtkinter as ctk
from const.texts import TEXTS
from const.colors import primary_color, primary_color_light
from utils.state import AppState

def load_frame_audio(frame_audio, state: AppState):
    # En CTK, frame_audio ya debería ser un CTkFrame para que los colores coincidan
    frame_audio.pack_propagate(False)
    frame_audio.grid_columnconfigure(0, weight=1)
    frame_audio.grid_columnconfigure(1, weight=1)


    ### Audio On/Off (CheckButton -> CTkCheckBox)
    audio_check = ctk.CTkCheckBox(
        frame_audio,
        text=TEXTS[state.lang.get()]["audio"],
        variable=state.audio,
        command=state.save_audio,
        checkbox_width=20,
        checkbox_height=20,
        fg_color=primary_color
    )
    audio_check.grid(row=0, column=0, sticky='e', padx=10, pady=0)
    audio_check.variable = state.audio

    ### Music On/Off
    music_check = ctk.CTkCheckBox(
        frame_audio,
        text=TEXTS[state.lang.get()]["music"],
        variable=state.music,
        command=state.save_music,
        checkbox_width=20,
        checkbox_height=20,
        fg_color=primary_color
    )
    music_check.grid(row=0, column=1, sticky='e', padx=10, pady=0)
    music_check.variable = state.music
    

    # Fila 1: Etiqueta de volumen (Label -> CTkLabel)
    label_vol = ctk.CTkLabel(
        frame_audio, 
        text=TEXTS[state.lang.get()]["volume"], 
        text_color="white", 
    )
    label_vol.grid(row=1, column=0, columnspan=2, pady=(10, 0))

    # Fila 2: La barra (Scale -> CTkSlider)
    volume_scale = ctk.CTkSlider(
        frame_audio, 
        from_=0, 
        to=10, 
        number_of_steps=10,          # Para que se mueva de 1 en 1 como el Scale original
        variable=state.volume,
        fg_color="#1a1a1a",          # Color de la barra de fondo
        progress_color=primary_color, # Color de la barra que se va llenando
        button_color=primary_color,  # Color del círculo deslizante
        button_hover_color=primary_color_light,
        width=200,
        command=lambda v: state.save_volume(int(v))
    )
    volume_scale.grid(row=2, column=0, columnspan=2, sticky='n', pady=10)