from tkinter import Tk, Label, Frame
import tkinter
import customtkinter as ctk
from components.frame_lang import load_frame_lang
from components.frame_update import load_frame_update
from components.frame_window import load_frame_window
from components.frame_audio import load_frame_audio
from components.frame_server import load_frame_server
from components.frame_news import load_frame_news
from const.config import PROJECT_NAME
import base64
import os
from assets.icono_data import ICONO_BASE64
from assets.imagenes_launcher_data import HERO
from functions.functions import abrir_enlace, launch_game
from utils.image_converter import get_image_from_base64
import pywinstyles
from utils.state import AppState
from utils.styles import style
from const.colors import bg_color, primary_color
from const.config import app_width,app_heigh, VERSION, components_width, REGISTER_URL
from const.texts import TEXTS
from views.options_window import Options
from utils.tray import TrayIcon
from utils.process import listen_for_show_requests
from utils.launcher_settings import CLOSE_TO_TRAY, tray_hint_shown, set_tray_hint_shown
from utils.periodic import run_periodically
from utils.process import process_exists
from utils.logger import logger
from services.launcher_update_service import fetch_launcher_info, check_and_update_launcher
from updater import trigger_launcher_update
from const.config import UPDATE_CHECK_MS
from tkinter import messagebox
from pathlib import Path
import threading

class App():
    def __init__(self, register_url=None):
        # =========================
        # UI
        # =========================
        ctk.set_appearance_mode("dark")
        ctk.set_widget_scaling(1.0)  # Los widgets no se agrandan por el zoom de Windows
        ctk.set_window_scaling(1.0)  # La ventana mantiene su tamaño exacto en píxeles
        root = ctk.CTk()
        #root.overrideredirect(True) #Elimina la barra de ventana
        root.title(PROJECT_NAME)

        x = root.winfo_screenmmwidth() *  2
        y = int(root.winfo_screenheight() * 0.3)
        root.geometry(f"{app_width}x{app_heigh}+"+ str(x) + '+' + str(y))
        root.resizable(False, False)
        
        img_icon_data = base64.b64decode(ICONO_BASE64)
        with open("temp_icon.ico", "wb") as tmp:
            tmp.write(img_icon_data)
        root.iconbitmap("temp_icon.ico")
        os.remove("temp_icon.ico")
        style(root)
        root.config(bg=bg_color)
        root.attributes("-alpha", 0.9)

        #Creo el estado de la app
        state = AppState()

        # --- Cargar y usar un logo (ejemplo) ---
        # Puedes ajustar el tamaño o no pasarlo si quieres el tamaño original
        logo_mu_image_tk = get_image_from_base64(HERO, size=(app_width, 150))
        logo_label = Label(root, image=logo_mu_image_tk, bd=0) # bd=0 para que no tenga borde
        logo_label.pack(pady=0) # Ejemplo de posicionamiento

        
        # Titulo
        Label(
            root,
            text=PROJECT_NAME,
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg="white",
        ).pack(pady=(8, 10))

        # xxxxxxxxxxxxxxxxx
        # Botón jugar
        # xxxxxxxxxxxxxxxxx
        btn_container = ctk.CTkFrame(root, fg_color="black")
        

        frame_btn_play = ctk.CTkFrame(btn_container, width=210, height=40, fg_color="black")
        frame_btn_play.grid(row=0, column=0)
        frame_btn_play.pack_propagate(False)
        
        btn_play = ctk.CTkButton(
            frame_btn_play,
            text=f"{TEXTS[state.lang.get()]['play']}     ",
            height=40,
            width=components_width,
            anchor=tkinter.CENTER,
            fg_color=primary_color,
            state="normal" if state.can_launch == False else "normal", # Lo habilitaremos una vez cargados los servidores
        )

        def play():
            launched = launch_game(
                # server_var.get(),
                "Online",
                state.window_mode.get(),
                state.resolution.get(),
                state.audio.get(),
                state.music.get(),
                state.volume.get(),
                state.lang.get(),
                btn_play,
                root
            )
            # Como Steam/Battle.net: con el juego abierto, el launcher se va a la bandeja
            if launched and state.close_action.get() == CLOSE_TO_TRAY:
                root.after(1000, hide_to_tray)

        btn_play.configure(command=play)
        btn_play.place(x=0, y=0)

        # --- BOTÓN CONFIG (Lado Derecho) ---
        # El frame mide 40, el botón 50. Al moverlo x=-10, ocultamos el redondeo izquierdo.
        frame_btn_cfg = ctk.CTkFrame(btn_container, width=40, height=40, fg_color="transparent")
        frame_btn_cfg.grid(row=0, column=1)
        frame_btn_cfg.pack_propagate(False)

        btn_cfg = ctk.CTkButton(
            frame_btn_cfg, 
            text="     ⚙️",
            width=55, # Un poco más ancho para que sobre por la izquierda
            height=40,
            fg_color=primary_color,
            anchor=tkinter.CENTER,
            cursor="hand2",
            command=lambda: Options(state, root) # Abrir ventana de opciones
        )
        # El truco: lo desplazamos a la izquierda para "esconder" su redondeo en el borde del frame
        btn_cfg.place(x=-15, y=0) 

        # -------- FRAMES -----------------------------
        # Resolución, audio e idioma están en Options: acá van las noticias
        frame_news = Frame(root, bg=bg_color)
        frame_server = Frame(root, bg=bg_color)
        frame_update = Frame(root, bg=bg_color)

        frame_news.pack(fill="x", pady=(0, 12))
        frame_server.pack(fill="x", pady=(0, 6))
        frame_update.pack(fill="x", pady=(0, 8))

        load_frame_news(frame_news, state)
        load_frame_server(frame_server, state, btn_play)
        load_frame_update(frame_update, state, btn_play,
                          on_client_update=lambda: notify_if_hidden(get_txt("client_update_notify")))

        #Aqc'a cargo el btn a la GUI
        btn_container.pack()

        # Enlace
        label = Label(root, text=TEXTS[state.lang.get()]["register"], fg="dodger blue", cursor="hand2", font=("Arial", 10))
        label.config(bg=bg_color, pady=10)
        label.pack(pady=(10, 0))
        label.bind(
            "<Button-1>",
            lambda event: abrir_enlace(event, register_url or REGISTER_URL)
        )

        version = Label(root, text=f"{TEXTS.get(state.lang.get(), TEXTS['Spn'])['version']}: {VERSION}", fg="white", font=("Courier New", 8))
        version.config(bg=bg_color, fg="#adadad", pady=2)
        # Pegada al borde inferior de la ventana
        version.pack(side="bottom", pady=(0, 4))

        # -------- NUEVA VERSIÓN DEL LAUNCHER ----------
        # Al iniciar ya se actualiza solo. Si sale una versión con el launcher abierto,
        # no se reinicia por su cuenta (podría estar jugando): la versión pasa a ser
        # un enlace "Actualizar a X" y, si está en la bandeja, se avisa con una notificación.
        launcher_update = {"version": None, "notified": None, "applying": False}

        def refresh_version_label(*args):
            txts = TEXTS.get(state.lang.get(), TEXTS["Spn"])
            text = f"{txts.get('version', 'Versión')}: {VERSION}"
            if launcher_update["applying"]:
                version.config(text=txts.get("launcher_updating", "Actualizando launcher..."),
                               fg="#adadad", cursor="")
            elif launcher_update["version"]:
                version.config(text=f"{text}  ·  {txts.get('launcher_update_link', 'Actualizar a')} "
                                    f"{launcher_update['version']}",
                               fg="dodger blue", cursor="hand2")
            else:
                version.config(text=text, fg="#adadad", cursor="")

        def on_launcher_info(info):
            if not info:
                return  # sin conexión: se reintenta en el próximo chequeo
            new_version = str(info.get("version") or "") if info.get("needUpdate") else None
            if new_version != launcher_update["version"]:
                launcher_update["version"] = new_version
                refresh_version_label()
            if new_version and launcher_update["notified"] != new_version:
                launcher_update["notified"] = new_version
                logger.info(f"Nueva versión del launcher disponible: {new_version}")
                notify_if_hidden(get_txt("launcher_update_notify").format(version=new_version))

        def apply_launcher_update(event=None):
            if not launcher_update["version"] or launcher_update["applying"]:
                return
            # El juego depende del mutex del launcher: no se reemplaza con el juego abierto
            if process_exists("main.exe"):
                messagebox.showinfo(PROJECT_NAME, get_txt("close_game_first"), parent=root)
                return
            launcher_update["applying"] = True
            refresh_version_label()

            def worker():
                info = check_and_update_launcher()
                try:
                    root.after(0, finish_launcher_update, info)
                except Exception:
                    pass

            threading.Thread(target=worker, daemon=True, name="launcher-update").start()

        def finish_launcher_update(info):
            new_path = info.get("_new_launcher_path") if info else None
            if not new_path:
                launcher_update["applying"] = False
                refresh_version_label()
                messagebox.showerror(PROJECT_NAME, get_txt("launcher_update_error"), parent=root)
                return
            tray.stop()
            # Lanza el updater y termina este proceso (sys.exit sale del mainloop)
            trigger_launcher_update(
                Path(new_path),
                Path(info["_current_exe"]),
                Path(info["_updater_path"]) if info.get("_updater_path") else None,
            )

        version.bind("<Button-1>", apply_launcher_update)

        def update_app_texts(*args):
            lang = state.lang.get()
            txts = TEXTS.get(lang, TEXTS["Spn"])
            btn_play.configure(text=f"{txts.get('play', 'JUGAR')}     ")
            label.config(text=txts.get("register", "Registrarse"))
            refresh_version_label()

        state.lang.trace_add("write", update_app_texts)

        # -------- BANDEJA DEL SISTEMA ----------------
        def get_txt(key, fallback=""):
            return TEXTS.get(state.lang.get(), TEXTS["Spn"]).get(key, fallback)

        tray = TrayIcon(root, PROJECT_NAME, state.lang.get(), on_play=lambda: btn_play.invoke())
        # El menú de la bandeja corre en otro hilo: recibe el idioma como texto, no el StringVar
        state.lang.trace_add("write", lambda *args: tray.set_lang(state.lang.get()))

        def hide_to_tray():
            tray.hide()
            if tray.available and not tray_hint_shown():
                tray.notify(get_txt("tray_hint"), PROJECT_NAME)
                set_tray_hint_shown()

        def notify_if_hidden(message):
            # Con la ventana visible alcanza con el aviso en pantalla
            if tray.available and root.state() in ("withdrawn", "iconic"):
                tray.notify(message, PROJECT_NAME)

        run_periodically(root, UPDATE_CHECK_MS, fetch_launcher_info, on_launcher_info,
                         name="launcher-update-check")

        def on_close():
            if state.close_action.get() == CLOSE_TO_TRAY and tray.available:
                hide_to_tray()
            else:
                tray.quit()

        root.protocol("WM_DELETE_WINDOW", on_close)
        # Si se abre launcher.exe otra vez, esta instancia muestra su ventana
        listen_for_show_requests(lambda: tray.post(tray.show))

        pywinstyles.change_header_color(root, "#000000")
        try:
            root.mainloop()
        finally:
            tray.stop()

