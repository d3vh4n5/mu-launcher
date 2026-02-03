import base64
import os
from PIL import Image, ImageTk

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

def convertir_imagen_a_py(archivo_entrada, nombre_variable, archivo_salida='imagen_data.py'):
    """
    Convierte una imagen (PNG, GIF, JPG) a una cadena Base64
    y la guarda en un archivo .py como una variable.
    """
    try:
        with open(archivo_entrada, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        
        # Modo 'a' para añadir al archivo existente, 'w' si quieres sobrescribir
        # Si vas a tener varias imágenes, es mejor usar 'a'
        with open(archivo_salida, 'a') as f:
            f.write(f'\n# Datos para {os.path.basename(archivo_entrada)}\n')
            f.write(f'{nombre_variable} = "{encoded}"\n')
        
        print(f"✅ ¡Éxito! La imagen '{archivo_entrada}' ha sido convertida y añadida a '{archivo_salida}' como la variable '{nombre_variable}'.")
    except FileNotFoundError:
        print(f"❌ Error: El archivo '{archivo_entrada}' no se encontró.")
    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")

if __name__ == "__main__":
    # --- USO ---
    # Ejemplo si tienes un archivo "fondo_launcher.png" y quieres que se llame BACKGROUND_IMAGE_BASE64
    convertir_imagen_a_py('fondo_launcher.png', 'BACKGROUND_IMAGE_BASE64', 'imagenes_launcher_data.py')

    # Si tienes otra imagen, por ejemplo, un logo "logo_mu.png"
    convertir_imagen_a_py('logo_mu.jpg', 'LOGO_MU_BASE64', 'imagenes_launcher_data.py')

    # Si quieres volver a generar el archivo desde cero, cambia 'a' por 'w' en la línea 17
    # o borra 'imagenes_launcher_data.py' antes de correr el script.