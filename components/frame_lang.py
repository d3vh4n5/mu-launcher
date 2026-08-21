import customtkinter as ctk
from const.colors import primary_color, primary_color_light
from utils.state import AppState

def load_frame_lang(frame_idioma, state: AppState):
    frame_idioma.grid_columnconfigure(0, weight=1)
    frame_idioma.grid_columnconfigure(1, weight=1)
    frame_idioma.grid_columnconfigure(2, weight=1)

    def on_lang_select():
        state.save_lang()

    rb_spn = ctk.CTkRadioButton(
        frame_idioma,
        text="Esp",
        value="Spn",
        variable=state.lang,
        fg_color=primary_color,
        hover_color=primary_color_light,
        command=on_lang_select
    )
    rb_eng = ctk.CTkRadioButton(
        frame_idioma,
        text="Eng",
        value="Eng",
        variable=state.lang,
        fg_color=primary_color,
        hover_color=primary_color_light,
        command=on_lang_select
    )
    rb_por = ctk.CTkRadioButton(
        frame_idioma,
        text="Por",
        value="Por",
        variable=state.lang,
        fg_color=primary_color,
        hover_color=primary_color_light,
        command=on_lang_select
    )

    rb_spn.grid(row=0, column=0, padx=5, pady=5)
    rb_eng.grid(row=0, column=1, padx=5, pady=5)
    rb_por.grid(row=0, column=2, padx=5, pady=5)