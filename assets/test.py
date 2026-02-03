import tkinter as tk
import base64
import os
from PIL import Image, ImageTk # Necesitarás 'Pillow' para PNG/JPG
from icono_data import ICONO_BASE64
from imagenes_launcher_data import BACKGROUND_IMAGE_BASE64, LOGO_MU_BASE64 # Importa tus variables aquí

# --- Instalación de Pillow si no la tienes ---
# pip install Pillow

def get_image_from_base64(base64_string, size=None):
    """Decodifica una cadena Base64 a un objeto PhotoImage o ImageTk.PhotoImage."""
    img_data = base64.b64decode(base64_string)
    # Pillow necesita un objeto BytesIO para abrir datos binarios desde la memoria
    from io import BytesIO
    img_file = BytesIO(img_data)
    
    # Abrimos con Pillow
    pil_image = Image.open(img_file)

    if size:
        pil_image = pil_image.resize(size, Image.LANCZOS) # Llama a Image.LANCZOS directamente

    return ImageTk.PhotoImage(pil_image)

# --- Tu código del Launcher ---
root = tk.Tk()

# Configurar el icono de la ventana (como ya lo hiciste)
img_icon_data = base64.b64decode(ICONO_BASE64)
with open("temp_icon.ico", "wb") as tmp:
    tmp.write(img_icon_data)
root.iconbitmap("temp_icon.ico")
os.remove("temp_icon.ico") 

root.title("Mu 99b Launcher")
root.geometry("400x600") # Un tamaño de ejemplo para la ventana

# --- Cargar y usar la imagen de fondo ---
# Puedes pasar un tamaño si quieres que la imagen se redimensione automáticamente
background_image_tk = get_image_from_base64(BACKGROUND_IMAGE_BASE64, size=(800, 600)) 
background_label = tk.Label(root, image=background_image_tk)
background_label.place(x=0, y=0, relwidth=1, relheight=1) # Para que ocupe todo el fondo

# --- Cargar y usar un logo (ejemplo) ---
# Puedes ajustar el tamaño o no pasarlo si quieres el tamaño original
logo_mu_image_tk = get_image_from_base64(LOGO_MU_BASE64, size=(400, 150))
logo_label = tk.Label(root, image=logo_mu_image_tk, bd=0) # bd=0 para que no tenga borde
logo_label.pack(pady=0) # Ejemplo de posicionamiento

# Asegúrate de mantener una referencia a la imagen, sino Tkinter la borra
background_label.image = background_image_tk
logo_label.image = logo_mu_image_tk


# Otros widgets encima del fondo...
# Por ejemplo, un botón de "Jugar"
play_button = tk.Button(root, text="Jugar", font=("Arial", 16), command=lambda: print("¡Jugar!"))
play_button.pack(pady=50)


# Bucle principal de Tkinter
if __name__ == "__main__":
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Launcher cerrado por el usuario.")