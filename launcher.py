from views.app import App
from utils.process import process_exists
from tkinter import messagebox

if __name__ == "__main__":
    if process_exists('launcher.exe'):
        messagebox.showinfo("Proceso", "El proceso ya está en ejecución.")
    else:
        App()

