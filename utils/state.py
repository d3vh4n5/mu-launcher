from tkinter import BooleanVar, IntVar, StringVar

from const.config import RESOLUTION_MAP
from functions.functions import get_registry_value, set_reg_dword

mapa_invertido = {v: k for k, v in RESOLUTION_MAP.items()}

class AppState:
    def __init__(self):
        self.can_launch = False
        self.window_mode= BooleanVar(value=get_registry_value("WindowMode") == 1)
        val_registro = get_registry_value("Resolution")
        self.resolution = StringVar(
            value=mapa_invertido.get(val_registro, "800 x 600")
        )
        self.audio = BooleanVar(value=get_registry_value("SoundOnOff") == 1)
        self.music = BooleanVar(value=get_registry_value("MusicOnOff") == 1)
        self.volume = IntVar(value=get_registry_value("VolumeLevel") or 5)
        val_reg = get_registry_value("LangSelection")
        self.lang = StringVar(
            value=val_reg if val_reg in ["Spn", "Eng", "Por"] else "Eng"
        )

    def save_window_mode(self):
        val= 1 if self.window_mode.get() else 0
        set_reg_dword("WindowMode", val)
        
    def save_resolution(self, event):
        val = RESOLUTION_MAP[self.resolution.get()]
        set_reg_dword("Resolution", val)
    
    def save_audio(self):
        val= 1 if self.window_mode.get() else 0
        set_reg_dword("SoundOnOff", val)
    
    def save_music(self):
        val= 1 if self.window_mode.get() else 0
        set_reg_dword("MusicOnOff", val)
    
    def save_volume(self, val:int):
        set_reg_dword("VolumeLevel", val)

    def save_lang(self):
        set_reg_dword("LangSelection", self.lang.get(), "REG_SZ")
    
    def set_can_launch(self, value: bool):
        self.can_launch = value