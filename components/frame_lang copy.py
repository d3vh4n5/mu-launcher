from const.colors import primary_color
from tkinter import Radiobutton
from customtkinter import CTkRadioButton
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
                rb.configure(fg_color=primary_color) # Color para el seleccionado
            else:
                rb.configure(fg_color="white") # Color para los no seleccionados

    # Estilo base (sin el fg dinámico aquí)
    lang_style = {
        "variable": state.lang,
        #"font": ("Arial", 10),
        # En CTk el color de fondo se mezcla con el frame automáticamente
        #"fg_color": "#D4AF37",      # El color del círculo cuando está MARCADO
        #"border_color": "white",    # El color del borde cuando está DESMARCADO
        #"hover_color": "#AA8A2E",   # Color al pasar el mouse
        #"text_color": "white",      # Color de la letra
        # El comando ahora es directo
        "command": lambda: [state.save_lang(), update_radio_colors()] # Guarda el estado y luego actualiza los colores
    }

    # Creamos los Radiobuttons y los guardamos en la lista
    rb_spn = CTkRadioButton(frame_idioma, text="Esp", value="Spn", **lang_style)
    rb_eng = CTkRadioButton(frame_idioma, text="Eng", value="Eng", **lang_style)
    rb_por = CTkRadioButton(frame_idioma, text="Por", value="Por", **lang_style)

    radios.extend([rb_spn, rb_eng, rb_por])

    # Posicionamos en el grid
    rb_spn.grid(row=0, column=0, padx=(30, 0))
    rb_eng.grid(row=0, column=1)
    rb_por.grid(row=0, column=2)

    # Llamamos a la función una vez al inicio para que el cargado desde el registro pinte el correcto
    update_radio_colors()