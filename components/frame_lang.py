from const.colors import primary_color
from tkinter import Radiobutton
from utils.state import AppState


def load_frame_lang(frame_idioma, state: AppState):
    frame_idioma.grid_columnconfigure(0, weight=1)
    frame_idioma.grid_columnconfigure(1, weight=1)
    frame_idioma.grid_columnconfigure(2, weight=1)

    # Creamos una lista para guardar las referencias de los Radiobuttons
    radios = []

    def update_radio_colors():
        """Cambia el color de todos los radios basándose en la selección actual"""
        seleccionado = state.lang.get()
        for rb in radios:
            # rb.cget("value") nos da el 'value' que le asignamos (Spn, Eng, o Por)
            if rb.cget("value") == seleccionado:
                rb.config(fg=primary_color) # Color para el seleccionado
            else:
                rb.config(fg="white") # Color para los no seleccionados

    # Estilo base (sin el fg dinámico aquí)
    lang_style = {
        "variable": state.lang,
        "bg": "black",
        "selectcolor": "black",
        "activebackground": "black",
        "activeforeground": "white",
        "highlightthickness": 0,
        "font": ("Arial", 10),
        # Ejecutamos el guardado y LUEGO actualizamos los colores locales
        "command": lambda: [state.save_lang(), update_radio_colors()]
    }

    # Creamos los Radiobuttons y los guardamos en la lista
    rb_spn = Radiobutton(frame_idioma, text="Español", value="Spn", **lang_style)
    rb_eng = Radiobutton(frame_idioma, text="English", value="Eng", **lang_style)
    rb_por = Radiobutton(frame_idioma, text="Português", value="Por", **lang_style)

    radios.extend([rb_spn, rb_eng, rb_por])

    # Posicionamos en el grid
    rb_spn.grid(row=0, column=0)
    rb_eng.grid(row=0, column=1)
    rb_por.grid(row=0, column=2)

    # Llamamos a la función una vez al inicio para que el cargado desde el registro pinte el correcto
    update_radio_colors()