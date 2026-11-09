from tkinter import Label, Frame
import tkinter
import customtkinter as ctk
from components.frame_lang import load_frame_lang
from components.frame_window import load_frame_window
from components.frame_audio import load_frame_audio
import pywinstyles
from utils.window_icon import set_window_icon
from utils.state import AppState
from utils.styles import style
from const.colors import bg_color, primary_color
from const.config import app_width, components_width

from const.texts import TEXTS

class Options(ctk.CTkToplevel):
    def __init__(self, app_state: AppState, parent=None):
        super().__init__(parent)
        self.app_state = app_state

        def get_txt(key, fallback=""):
            lang = self.app_state.lang.get()
            return TEXTS.get(lang, TEXTS.get("Spn", {})).get(key, fallback)

        txt_options = get_txt("options_title", "Opciones")
        self.title(txt_options)
        x = self.winfo_screenmmwidth() *  2
        y = int(self.winfo_screenheight() * 0.3)
        self.geometry(f"{app_width}x500+"+ str(x) + '+' + str(y))
        self.resizable(False, False)
        self.configure(fg_color=bg_color)
        self.attributes("-alpha", 0.95)

        if parent:
            self.transient(parent)
            self.grab_set()

        # CTkToplevel pone su ícono propio a los 200 ms: aplicamos el nuestro después
        set_window_icon(self, delay_ms=250)

        style(self)

        # Titulo
        self.lbl_title = Label(
            self,
            text=txt_options,
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg="white",
        )
        self.lbl_title.pack(pady=10)

        # -------- FRAMES -----------------------------
        frame_window = Frame(self, width=app_width, bg=bg_color)
        frame_audio = Frame(self, width=app_width, bg="#0A0A0A", pady=10)
        frame_idioma = Frame(self, bg=bg_color)

        for frame in [frame_window, frame_audio, frame_idioma]:
            frame.pack(fill="x", pady=10)

        load_frame_window(frame_window, app_state)
        load_frame_audio(frame_audio, app_state)
        load_frame_lang(frame_idioma, app_state)

        self.btn_save = ctk.CTkButton(
            self,
            text=get_txt("save", "Guardar"),
            width=components_width,
            anchor=tkinter.CENTER,
            fg_color=primary_color,
            command=self.save_and_close
        )
        self.btn_save.pack(pady=10)

        def update_options_lang(*args):
            t_opt = get_txt("options_title", "Opciones")
            t_save = get_txt("save", "Guardar")
            self.title(t_opt)
            self.lbl_title.config(text=t_opt)
            self.btn_save.configure(text=t_save)

        self.app_state.lang.trace_add("write", update_options_lang)

        try:
            pywinstyles.change_header_color(self, "#000000")
        except Exception:
            pass

    def save_and_close(self):
        self.app_state.save_all()
        self.destroy()


