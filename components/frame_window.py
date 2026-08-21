from tkinter import HORIZONTAL, Frame, Scale, ttk, Checkbutton, BooleanVar, StringVar, Label, IntVar, Radiobutton
from customtkinter import CTkComboBox, CTkCheckBox
from const.colors import *
from const.config import RESOLUTION_MAP, components_width
from const.texts import TEXTS
from functions.functions import get_registry_value, abrir_enlace, set_reg_dword
from utils.state import AppState

def load_frame_window(frame1, state: AppState):
    def get_txt(key, fallback=""):
        return TEXTS.get(state.lang.get(), TEXTS["Spn"]).get(key, fallback)

    # resolucion
    lbl_res = Label(
        frame1,
        text=get_txt("resolution", "Resolución"),
        bg="black",
        fg="white",
    )
    lbl_res.pack()

    resolution_combo = CTkComboBox(
        frame1,
        variable=state.resolution,
        values=list(RESOLUTION_MAP.keys()),
        state="readonly",
        width=components_width,
        border_color=primary_color,
        button_color=primary_color,
        command=state.save_resolution
    )
    resolution_combo.pack(pady=5)
    resolution_combo.variable = state.resolution
    resolution_combo.set(state.resolution.get())

    # Modo ventana
    check = CTkCheckBox(
        frame1,
        text=get_txt("window_mode", "Modo Ventana"),
        variable=state.window_mode,
        command=state.save_window_mode,
        checkbox_width=20,
        checkbox_height=20,
        fg_color=primary_color
    )
    check.pack(pady=10)
    check.variable = state.window_mode

    def update_texts(*args):
        lbl_res.config(text=get_txt("resolution", "Resolución"))
        check.configure(text=get_txt("window_mode", "Modo Ventana"))

    state.lang.trace_add("write", update_texts)
