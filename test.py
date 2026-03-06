import customtkinter as ctk

app = ctk.CTk()
app.geometry("400x200")

# Contenedor principal para ambos botones
btn_container = ctk.CTkFrame(app, fg_color="transparent")
btn_container.pack(pady=50)

# --- BOTÓN PLAY (Lado Izquierdo) ---
# El frame mide 130, el botón 140. Al moverlo x=10, cortamos el redondeo derecho.
frame_btn_play = ctk.CTkFrame(btn_container, width=130, height=40, fg_color="transparent")
frame_btn_play.grid(row=0, column=0)
frame_btn_play.pack_propagate(False)

btn_play = ctk.CTkButton(
    frame_btn_play, 
    text="Jugar",
    width=140, 
    height=40,
)
btn_play.place(x=0, y=0) # El inicio es normal, el final (derecha) se corta por el frame

# --- BOTÓN CONFIG (Lado Derecho) ---
# El frame mide 40, el botón 50. Al moverlo x=-10, ocultamos el redondeo izquierdo.
frame_btn_pcfg = ctk.CTkFrame(btn_container, width=40, height=40, fg_color="transparent")
frame_btn_pcfg.grid(row=0, column=1)
frame_btn_pcfg.pack_propagate(False)

btn_pcfg = ctk.CTkButton(
    frame_btn_pcfg, 
    text="    ⚙️",
    width=55, # Un poco más ancho para que sobre por la izquierda
    height=40,
    anchor="center"
)
# El truco: lo desplazamos a la izquierda para "esconder" su redondeo en el borde del frame
btn_pcfg.place(x=-15, y=0) 

app.mainloop()