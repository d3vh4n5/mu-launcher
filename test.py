import customtkinter as ctk
import subprocess
import os

def lanzar_juego():
    if os.path.exists("main.exe"):
        subprocess.Popen("main.exe")
        app.destroy()
    else:
        print("Error: No se encuentra main.exe")

# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Mu Online Launcher")
app.geometry("400x500")

# Título
label = ctk.CTkLabel(app, text="MU ONLINE", font=("Arial", 30, "bold"))
label.pack(pady=40)

# Botón Jugar (con bordes redondeados y color personalizado)
btn_jugar = ctk.CTkButton(
    app, 
    text="JUGAR AHORA", 
    command=lanzar_juego,
    fg_color="#D4AF37",    # Color Dorado Mu
    hover_color="#AA8A2E", # Dorado oscuro al pasar el mouse
    text_color="black",
    font=("Arial", 16, "bold"),
    corner_radius=10,
    height=50
)
btn_jugar.pack(pady=20)

app.mainloop()