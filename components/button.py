from const.colors import *
from tkinter import Button
from const.colors import *

font_size=9

class ButtonWithHover():
    def __init__(self, frame, text, cmd): 
        self.btn = Button(
                frame,
                text=text,
                width=35,
                fg='white',
                bg=primary_color,
                command=cmd,
                font=("Arial", font_size, "bold")
            )
        self.btn.pack()
        self.btn.bind("<Enter>", self.on_hover)
        self.btn.bind("<Leave>", self.on_leave_accent)

    def on_hover(self, event):
        event.widget.configure(bg=primary_color_light, font=("Arial", font_size, "bold"))
    
    def on_leave(self, event):
        event.widget.configure(bg=primary_color, font=("Arial", font_size, "bold"))
    
    def on_leave_accent(self, event):
        event.widget.configure(bg=accent_color, font=("Arial", font_size, "bold"))