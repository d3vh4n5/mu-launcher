from tkinter import ttk

def style(root):
    style = ttk.Style()
    style.theme_use('clam') # 'clam' permite personalizar más que el tema por defecto

    # Configuramos el diseño del Combobox
    style.configure("TCombobox",
                    fieldbackground="black", # Fondo de la barra de texto
                    background="#003066",    # Fondo del botón de la flecha
                    foreground="white",      # Color del texto seleccionado
                    darkcolor="black",       # Bordes
                    lightcolor="#0F8CBD",
                    bordercolor="#003066",
                    insertcolor="white")     # Color del cursor

    # Cambiar el color cuando el mouse pasa por encima de la flecha
    style.map('TCombobox',
            background=[('active', '#007A29')],
            fieldbackground=[('readonly', 'black')])
    # Cambia el color de la lista desplegable (el Pop-up)
    root.option_add("*TCombobox*Listbox.background", "#313131")
    root.option_add("*TCombobox*Listbox.foreground", "white")
    root.option_add("*TCombobox*Listbox.selectBackground", "#00859C")
    root.option_add("*TCombobox*Listbox.selectForeground", "white")