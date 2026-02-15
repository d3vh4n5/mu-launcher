from const.colors import *
import tkinter
from const.colors import *
from customtkinter import CTkButton

font_size=10

class ButtonWithHover():
    def __init__(self, frame, text, cmd): 
        self.btn = CTkButton(
                frame,
                text=text,
                width=250,
                command=cmd,
                anchor=tkinter.CENTER
            )
        self.btn.pack(pady=(10, 0))
        # self.btn.bind("<Enter>", self.on_hover)
        # self.btn.bind("<Leave>", self.on_leave)

    def on_hover(self, event):
        event.widget.configure(bg=primary_color_light, font=("Arial", font_size, "bold"))
    
    def on_leave(self, event):
        event.widget.configure(bg=primary_color, font=("Arial", font_size, "bold"))
    
    def on_leave_accent(self, event):
        event.widget.configure(bg=accent_color, font=("Arial", font_size, "bold"))