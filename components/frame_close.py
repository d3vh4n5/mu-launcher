from tkinter import Label

import customtkinter as ctk

from const.colors import primary_color, primary_color_light
from const.texts import TEXTS
from utils.launcher_settings import CLOSE_EXIT, CLOSE_TO_TRAY
from utils.state import AppState


def load_frame_close(frame, state: AppState):
    """Opción de Options: qué hace la X de la ventana principal."""
    def get_txt(key, fallback=""):
        return TEXTS.get(state.lang.get(), TEXTS["Spn"]).get(key, fallback)

    lbl = Label(frame, text=get_txt("close_behavior", "Al cerrar la ventana"), bg="black", fg="white")
    lbl.pack()

    options = []
    for value, key, fallback in (
        (CLOSE_TO_TRAY, "close_to_tray", "Minimizar a la bandeja"),
        (CLOSE_EXIT, "close_exit", "Cerrar el launcher"),
    ):
        rb = ctk.CTkRadioButton(
            frame,
            text=get_txt(key, fallback),
            value=value,
            variable=state.close_action,
            fg_color=primary_color,
            hover_color=primary_color_light,
            command=state.save_close_action,
        )
        rb.pack(anchor="w", padx=60, pady=4)
        options.append((rb, key, fallback))

    def update_texts(*args):
        lbl.config(text=get_txt("close_behavior", "Al cerrar la ventana"))
        for rb, key, fallback in options:
            rb.configure(text=get_txt(key, fallback))

    state.lang.trace_add("write", update_texts)
