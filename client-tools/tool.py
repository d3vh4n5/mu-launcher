import os
import sys
import json
import threading
import base64
from pathlib import Path
from tkinter import filedialog

# Permite ejecutar este archivo directamente desde client-tools o desde otra carpeta.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = Path(__file__).resolve().parent
for _path in (PROJECT_ROOT, TOOLS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from tkinter import messagebox  # noqa: E402

from client_scan import (  # noqa: E402
    LAUNCHER_EXE,
    build_manifest,
    diff_plan,
    looks_like_client,
    scan_client,
    sha256_file,
)
from publish_api import PublishApi, PublishApiError, is_insecure_url  # noqa: E402

try:
    from const.config import MU_SERVER_URL as DEFAULT_SERVER_URL
except Exception:
    DEFAULT_SERVER_URL = None

import utils.wmi_guard  # noqa: F401  (debe ir antes de customtkinter)
import customtkinter as ctk

from assets.icono_data import ICONO_BASE64
from const.colors import bg_color, primary_color, primary_color_light

INPUT_COLOR = "#0A0A0A"
SURFACE_COLOR = "#111111"
TEXT_MUTED_COLOR = "#ADADAD"

class ClientToolsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("Herramientas de Cliente MU")
        self.geometry("560x760")
        self.resizable(False, False)
        self.configure(fg_color=bg_color)
        self._set_icon()

        # Tabview para las 2 herramientas
        self.tabview = ctk.CTkTabview(
            self,
            width=490,
            height=440,
            fg_color=SURFACE_COLOR,
            segmented_button_fg_color=INPUT_COLOR,
            segmented_button_selected_color=primary_color,
            segmented_button_selected_hover_color=primary_color_light,
            segmented_button_unselected_color=INPUT_COLOR,
            segmented_button_unselected_hover_color=primary_color_light,
        )
        self.tabview.pack(padx=15, pady=10, fill="both", expand=True)

        self.tab_manifest = self.tabview.add("Generador Manifest")
        self.tab_patcher = self.tabview.add("Parchador de Servidor")
        self.tab_publish = self.tabview.add("Publicar en servidor")

        self.setup_manifest_tab()
        self.setup_patcher_tab()
        self.setup_publish_tab()

    def _set_icon(self):
        try:
            from const.paths import TEMP_DIR
            icon_path = TEMP_DIR / "client_tools_icon.ico"
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            icon_path.write_bytes(base64.b64decode(ICONO_BASE64))
            self.iconbitmap(str(icon_path))
        except Exception:
            pass

    # ==========================================
    # TAB 1: GENERADOR DE MANIFEST
    # ==========================================
    def setup_manifest_tab(self):
        tab = self.tab_manifest

        # Directorio cliente
        lbl_dir = ctk.CTkLabel(tab, text="Carpeta del Cliente:", font=("Arial", 12, "bold"))
        lbl_dir.pack(anchor="w", padx=10, pady=(10, 2))

        frame_dir = ctk.CTkFrame(tab, fg_color="transparent")
        frame_dir.pack(fill="x", padx=10, pady=2)

        self.entry_client_dir = ctk.CTkEntry(
            frame_dir, width=350, fg_color=INPUT_COLOR, border_color=primary_color,
            text_color="white"
        )
        self.entry_client_dir.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_client_dir.insert(0, os.getcwd())

        btn_browse_dir = ctk.CTkButton(
            frame_dir, text="Examinar", width=80, fg_color=primary_color,
            hover_color=primary_color_light, command=self.browse_client_dir
        )
        btn_browse_dir.pack(side="right")

        # Versión manifest
        frame_version = ctk.CTkFrame(tab, fg_color="transparent")
        frame_version.pack(fill="x", padx=10, pady=5)

        lbl_ver = ctk.CTkLabel(frame_version, text="Versión Manifest:", font=("Arial", 11))
        lbl_ver.pack(side="left", padx=(0, 10))

        self.entry_manifest_ver = ctk.CTkEntry(
            frame_version, width=100, fg_color=INPUT_COLOR, border_color=primary_color,
            text_color="white"
        )
        self.entry_manifest_ver.pack(side="left")
        self.entry_manifest_ver.insert(0, "1.0.0")

        self.exclude_dirs = {
            "Logs": ctk.BooleanVar(value=True),
            "ScreenShots": ctk.BooleanVar(value=True),
            "Temp": ctk.BooleanVar(value=True),
            # "Launcher" NO: Data/Launcher (updater.exe, serverinfo/) se distribuye
            ".git": ctk.BooleanVar(value=True),
            "__pycache__": ctk.BooleanVar(value=True),
        }
        self.exclude_files = {
            "manifest.json": ctk.BooleanVar(value=True),
            "manifest.py": ctk.BooleanVar(value=True),
            "tool.py": ctk.BooleanVar(value=True),
            "tool.exe": ctk.BooleanVar(value=True),
            "MuError.dmp": ctk.BooleanVar(value=True),
            # Se actualiza por su propio flujo (API + updater), no por manifest
            "launcher.exe": ctk.BooleanVar(value=True),
        }

        exclusions_frame = ctk.CTkFrame(tab, fg_color=SURFACE_COLOR, corner_radius=6)
        exclusions_frame.pack(fill="both", expand=True, padx=10, pady=(8, 2))

        ctk.CTkLabel(
            exclusions_frame,
            text="Exclusiones del manifest",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(
            exclusions_frame,
            text="Marcadas = se ignoran al escanear",
            text_color=TEXT_MUTED_COLOR,
            font=("Arial", 10),
        ).pack(anchor="w", padx=10, pady=(0, 5))

        checks_frame = ctk.CTkScrollableFrame(
            exclusions_frame, height=180, fg_color=INPUT_COLOR
        )
        checks_frame.pack(fill="both", expand=True, padx=8, pady=5)
        self.exclusion_checks_frame = checks_frame

        ctk.CTkLabel(checks_frame, text="Directorios", font=("Arial", 11, "bold")).pack(
            anchor="w", padx=4, pady=(2, 0)
        )
        for name, variable in self.exclude_dirs.items():
            ctk.CTkCheckBox(
                checks_frame, text=name, variable=variable,
                fg_color=primary_color, hover_color=primary_color_light,
                border_color=primary_color,
            ).pack(
                anchor="w", padx=8, pady=2
            )

        ctk.CTkLabel(checks_frame, text="Archivos", font=("Arial", 11, "bold")).pack(
            anchor="w", padx=4, pady=(8, 0)
        )
        for name, variable in self.exclude_files.items():
            ctk.CTkCheckBox(
                checks_frame, text=name, variable=variable,
                fg_color=primary_color, hover_color=primary_color_light,
                border_color=primary_color,
            ).pack(
                anchor="w", padx=8, pady=2
            )

        custom_frame = ctk.CTkFrame(exclusions_frame, fg_color="transparent")
        custom_frame.pack(fill="x", padx=10, pady=(4, 8))
        self.entry_exclude_dir = ctk.CTkEntry(
            custom_frame, placeholder_text="Nuevo directorio", fg_color=INPUT_COLOR,
            border_color=primary_color, text_color="white"
        )
        self.entry_exclude_dir.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkButton(
            custom_frame, text="+ Directorio", width=105, fg_color=primary_color,
            hover_color=primary_color_light, command=self.add_exclude_dir
        ).pack(side="right")

        custom_file_frame = ctk.CTkFrame(exclusions_frame, fg_color="transparent")
        custom_file_frame.pack(fill="x", padx=10, pady=(0, 8))
        self.entry_exclude_file = ctk.CTkEntry(
            custom_file_frame, placeholder_text="Nuevo archivo", fg_color=INPUT_COLOR,
            border_color=primary_color, text_color="white"
        )
        self.entry_exclude_file.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkButton(
            custom_file_frame, text="+ Archivo", width=105, fg_color=primary_color,
            hover_color=primary_color_light, command=self.add_exclude_file
        ).pack(side="right")

        # Progreso y Estado
        self.lbl_manifest_status = ctk.CTkLabel(
            tab, text="Listo para generar manifest.json", text_color=TEXT_MUTED_COLOR
        )
        self.lbl_manifest_status.pack(padx=10, pady=(10, 2))

        self.progress_manifest = ctk.CTkProgressBar(
            tab, width=440, fg_color=INPUT_COLOR, progress_color=primary_color
        )
        self.progress_manifest.set(0)
        self.progress_manifest.pack(padx=10, pady=5)

        # Botón Generar
        self.btn_gen_manifest = ctk.CTkButton(
            tab,
            text="📦 Generar manifest.json",
            font=("Arial", 13, "bold"),
            fg_color=primary_color,
            hover_color=primary_color_light,
            command=self.start_generate_manifest
        )
        self.btn_gen_manifest.pack(padx=10, pady=15)

    def browse_client_dir(self):
        selected = filedialog.askdirectory(title="Selecciona la carpeta del cliente MU")
        if selected:
            self.entry_client_dir.delete(0, "end")
            self.entry_client_dir.insert(0, selected)

    def start_generate_manifest(self):
        threading.Thread(target=self._generate_manifest_worker, daemon=True).start()

    def add_exclude_dir(self):
        name = self.entry_exclude_dir.get().strip()
        existing_dirs = {item.casefold() for item in self.exclude_dirs}
        if name and name.casefold() not in existing_dirs:
            self.exclude_dirs[name] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.exclusion_checks_frame,
                text=name,
                variable=self.exclude_dirs[name],
                fg_color=primary_color,
                hover_color=primary_color_light,
                border_color=primary_color,
            ).pack(anchor="w", padx=8, pady=2)
            self.entry_exclude_dir.delete(0, "end")

    def add_exclude_file(self):
        name = self.entry_exclude_file.get().strip()
        existing_files = {item.casefold() for item in self.exclude_files}
        if name and name.casefold() not in existing_files:
            self.exclude_files[name] = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.exclusion_checks_frame,
                text=name,
                variable=self.exclude_files[name],
                fg_color=primary_color,
                hover_color=primary_color_light,
                border_color=primary_color,
            ).pack(anchor="w", padx=8, pady=2)
            self.entry_exclude_file.delete(0, "end")

    def _generate_manifest_worker(self):
        client_dir = self.entry_client_dir.get().strip()
        manifest_version = self.entry_manifest_ver.get().strip() or "1.0.0"

        if not os.path.isdir(client_dir):
            self.update_manifest_status("Error: Directorio del cliente no válido.", 0)
            return

        self.btn_gen_manifest.configure(state="disabled")
        self.update_manifest_status("Escaneando archivos...", 0.1)

        exclude_dirs, exclude_files = self.active_exclusions()

        try:
            files_manifest = scan_client(
                client_dir, exclude_dirs, exclude_files,
                on_progress=lambda i, total, rel: self.update_manifest_status(
                    f"Procesando ({i}/{total}): {rel}", i / total
                ),
            )
        except OSError as e:
            self.update_manifest_status(f"Error leyendo archivos: {e}", 0)
            self.btn_gen_manifest.configure(state="normal")
            return

        if not files_manifest:
            self.update_manifest_status("No se encontraron archivos para incluir.", 0)
            self.btn_gen_manifest.configure(state="normal")
            return

        manifest = build_manifest(files_manifest, manifest_version)

        output_path = os.path.join(client_dir, "manifest.json")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            self.update_manifest_status(f"✅ ¡Manifest generado con éxito ({len(files_manifest)} archivos)!", 1.0)
        except Exception as e:
            self.update_manifest_status(f"Error guardando manifest.json: {e}", 0)
        finally:
            self.btn_gen_manifest.configure(state="normal")

    def active_exclusions(self):
        """Exclusiones tildadas en la pestaña Generador (las usa también Publicar)."""
        exclude_dirs = {n.casefold() for n, v in self.exclude_dirs.items() if v.get()}
        exclude_files = {n.casefold() for n, v in self.exclude_files.items() if v.get()}
        return exclude_dirs, exclude_files

    def update_manifest_status(self, text, progress=None):
        def _update():
            self.lbl_manifest_status.configure(text=text)
            if progress is not None:
                self.progress_manifest.set(progress)
        self.after(0, _update)

    # ==========================================
    # TAB 2: PARCHADOR DE SERVIDOR (BMD)
    # ==========================================
    def setup_patcher_tab(self):
        tab = self.tab_patcher

        lbl_info = ctk.CTkLabel(
            tab,
            text="Reemplaza el nombre del servidor en archivos Text_*.bmd",
            font=("Arial", 11), text_color=TEXT_MUTED_COLOR
        )
        lbl_info.pack(anchor="w", padx=10, pady=(10, 5))

        # Texto a buscar (Viejo)
        lbl_old = ctk.CTkLabel(tab, text="Texto original a buscar:", font=("Arial", 12, "bold"))
        lbl_old.pack(anchor="w", padx=10, pady=(5, 2))

        self.entry_old_str = ctk.CTkEntry(
            tab, width=440, fg_color=INPUT_COLOR, border_color=primary_color,
            text_color="white"
        )
        self.entry_old_str.pack(padx=10, pady=2)
        self.entry_old_str.insert(0, "SSeMU")

        # Texto a poner (Nuevo)
        lbl_new = ctk.CTkLabel(tab, text="Nuevo nombre del servidor:", font=("Arial", 12, "bold"))
        lbl_new.pack(anchor="w", padx=10, pady=(10, 2))

        self.entry_new_str = ctk.CTkEntry(
            tab, width=440, fg_color=INPUT_COLOR, border_color=primary_color,
            text_color="white"
        )
        self.entry_new_str.pack(padx=10, pady=2)
        self.entry_new_str.insert(0, "Mu Campana")

        # Archivos objetivo
        lbl_target = ctk.CTkLabel(tab, text="Carpeta de archivos BMD:", font=("Arial", 12, "bold"))
        lbl_target.pack(anchor="w", padx=10, pady=(10, 2))

        frame_bmd = ctk.CTkFrame(tab, fg_color="transparent")
        frame_bmd.pack(fill="x", padx=10, pady=2)

        self.entry_bmd_dir = ctk.CTkEntry(
            frame_bmd, width=350, fg_color=INPUT_COLOR, border_color=primary_color,
            text_color="white"
        )
        self.entry_bmd_dir.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_bmd_dir.insert(0, os.getcwd())

        btn_browse_bmd = ctk.CTkButton(
            frame_bmd, text="Examinar", width=80, fg_color=primary_color,
            hover_color=primary_color_light, command=self.browse_bmd_dir
        )
        btn_browse_bmd.pack(side="right")

        # Estado del parcheador
        self.lbl_patcher_status = ctk.CTkLabel(
            tab, text="Listo para aplicar parche.", text_color=TEXT_MUTED_COLOR
        )
        self.lbl_patcher_status.pack(padx=10, pady=(10, 5))

        # Botón Parchar
        self.btn_patch = ctk.CTkButton(
            tab,
            text="⚡ Parchar Nombre en Text_*.bmd",
            font=("Arial", 13, "bold"),
            fg_color=primary_color,
            hover_color=primary_color_light,
            command=self.start_patching
        )
        self.btn_patch.pack(padx=10, pady=15)

    def browse_bmd_dir(self):
        selected = filedialog.askdirectory(title="Selecciona la carpeta donde están los archivos Text_*.bmd")
        if selected:
            self.entry_bmd_dir.delete(0, "end")
            self.entry_bmd_dir.insert(0, selected)

    def start_patching(self):
        threading.Thread(target=self._patch_worker, daemon=True).start()

    def _patch_worker(self):
        old_str = self.entry_old_str.get()
        new_str = self.entry_new_str.get()
        bmd_dir = self.entry_bmd_dir.get().strip()

        if not old_str or not new_str:
            self.update_patcher_status("Error: Ingresa el texto viejo y nuevo.")
            return

        if not os.path.isdir(bmd_dir):
            self.update_patcher_status("Error: Carpeta no válida.")
            return

        self.btn_patch.configure(state="disabled")
        self.update_patcher_status("Buscando archivos Text_*.bmd...")

        target_files = ["Text_Eng.bmd", "Text_Por.bmd", "Text_Spn.bmd"]
        KEY = [0xFC, 0xCF, 0xAB]
        patched_count = 0

        for bmd_name in target_files:
            file_path = os.path.join(bmd_dir, bmd_name)
            if not os.path.exists(file_path):
                alt_path = os.path.join(bmd_dir, "Data", "Local", bmd_name)
                if os.path.exists(alt_path):
                    file_path = alt_path
                else:
                    continue

            try:
                with open(file_path, "rb") as f:
                    data = bytearray(f.read())

                found = 0
                i = 0
                while i < len(data) - len(old_str):
                    match = True
                    for j in range(len(old_str)):
                        decrypted_char = data[i+j] ^ KEY[(i+j) % 3]
                        if chr(decrypted_char) != old_str[j]:
                            match = False
                            break

                    if match:
                        found += 1
                        for j in range(len(new_str)):
                            encrypted_char = ord(new_str[j]) ^ KEY[(i+j) % 3]
                            data[i+j] = encrypted_char

                        padding_len = len(old_str) - len(new_str)
                        for j in range(max(0, padding_len)):
                            pos = i + len(new_str) + j
                            data[pos] = 0x00 ^ KEY[pos % 3]

                        i += len(old_str)
                    else:
                        i += 1

                if found > 0:
                    with open(file_path, "wb") as f:
                        f.write(data)
                    patched_count += 1
            except Exception as e:
                print(f"Error parchando {bmd_name}: {e}")

        if patched_count > 0:
            self.update_patcher_status(f"✅ ¡Parche aplicado con éxito en {patched_count} archivos!")
        else:
            self.update_patcher_status(f"No se encontró '{old_str}' o no existen los archivos Text_*.bmd.")

        self.btn_patch.configure(state="normal")

    def update_patcher_status(self, text):
        def _update():
            self.lbl_patcher_status.configure(text=text)
        self.after(0, _update)


    # ==========================================
    # TAB 3: PUBLICAR EN SERVIDOR
    # ==========================================
    def setup_publish_tab(self):
        tab = self.tab_publish
        entry_style = dict(fg_color=INPUT_COLOR, border_color=primary_color, text_color="white")
        button_style = dict(fg_color=primary_color, hover_color=primary_color_light)

        def row(label):
            frame = ctk.CTkFrame(tab, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(frame, text=label, width=120, anchor="w",
                         font=("Arial", 12, "bold")).pack(side="left")
            return frame

        frame = row("Carpeta cliente:")
        self.entry_publish_dir = ctk.CTkEntry(frame, **entry_style)
        self.entry_publish_dir.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_publish_dir.insert(0, os.getcwd())
        ctk.CTkButton(frame, text="Examinar", width=80, command=self.browse_publish_dir,
                      **button_style).pack(side="right")

        frame = row("Servidor:")
        self.entry_server_url = ctk.CTkEntry(frame, **entry_style)
        self.entry_server_url.pack(side="left", fill="x", expand=True)
        if DEFAULT_SERVER_URL:
            self.entry_server_url.insert(0, DEFAULT_SERVER_URL)

        frame = row("API key:")
        # No se guarda en ningún lado: hay que escribirla en cada sesión.
        self.entry_api_key = ctk.CTkEntry(frame, show="•", **entry_style)
        self.entry_api_key.pack(side="left", fill="x", expand=True)

        frame = row("Versión manifest:")
        self.entry_publish_ver = ctk.CTkEntry(frame, width=100, **entry_style)
        self.entry_publish_ver.pack(side="left")
        self.entry_publish_ver.insert(0, "1.0.0")

        self.publish_mode = ctk.StringVar(value="add")
        mode_frame = ctk.CTkFrame(tab, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=(6, 0))
        for value, text in (("add", "Solo agregar/reemplazar"),
                            ("mirror", "Espejo (borra lo que no está local)")):
            ctk.CTkRadioButton(mode_frame, text=text, value=value, variable=self.publish_mode,
                               fg_color=primary_color, hover_color=primary_color_light,
                               border_color=primary_color).pack(side="left", padx=(0, 12))

        self.include_launcher = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(tab, text="Incluir launcher.exe", variable=self.include_launcher,
                        fg_color=primary_color, hover_color=primary_color_light,
                        border_color=primary_color).pack(anchor="w", padx=10, pady=6)

        self.btn_compare = ctk.CTkButton(tab, text="🔍 Comparar con servidor",
                                         command=self.start_compare, **button_style)
        self.btn_compare.pack(padx=10, pady=4)

        self.lbl_publish_summary = ctk.CTkLabel(tab, text="", font=("Arial", 12, "bold"))
        self.lbl_publish_summary.pack(padx=10)

        self.txt_publish_changes = ctk.CTkTextbox(tab, height=150, fg_color=INPUT_COLOR,
                                                  font=("Consolas", 11))
        self.txt_publish_changes.pack(fill="both", expand=True, padx=10, pady=4)
        self.txt_publish_changes.configure(state="disabled")

        self.lbl_publish_status = ctk.CTkLabel(
            tab, text="Compará antes de publicar.", text_color=TEXT_MUTED_COLOR, wraplength=480
        )
        self.lbl_publish_status.pack(padx=10)

        self.progress_publish = ctk.CTkProgressBar(tab, width=440, fg_color=INPUT_COLOR,
                                                   progress_color=primary_color)
        self.progress_publish.set(0)
        self.progress_publish.pack(padx=10, pady=4)

        self.btn_publish = ctk.CTkButton(tab, text="🚀 Publicar", font=("Arial", 13, "bold"),
                                         state="disabled", command=self.start_publish,
                                         **button_style)
        self.btn_publish.pack(padx=10, pady=(4, 10))

        # Resultado de la última comparación; se invalida si cambian las opciones.
        self.publish_plan = None
        self.publish_mode.trace_add("write", lambda *_: self.invalidate_publish_plan())
        self.include_launcher.trace_add("write", lambda *_: self.invalidate_publish_plan())
        self.entry_publish_dir.bind("<KeyRelease>", lambda _e: self.invalidate_publish_plan())

    def browse_publish_dir(self):
        selected = filedialog.askdirectory(title="Selecciona la carpeta del cliente MU")
        if selected:
            self.entry_publish_dir.delete(0, "end")
            self.entry_publish_dir.insert(0, selected)
            self.invalidate_publish_plan()

    def invalidate_publish_plan(self):
        if self.publish_plan is not None:
            self.publish_plan = None
            self.btn_publish.configure(state="disabled")
            self.update_publish_status("Cambiaron las opciones: volvé a comparar.", 0)

    def publish_inputs(self):
        """(client_dir, api) o lanza PublishApiError con un mensaje para la UI."""
        client_dir = self.entry_publish_dir.get().strip()
        server = self.entry_server_url.get().strip()
        api_key = self.entry_api_key.get().strip()
        if not os.path.isdir(client_dir):
            raise PublishApiError("La carpeta del cliente no existe.")
        if not looks_like_client(client_dir):
            raise PublishApiError("La carpeta no parece un cliente: no tiene main.exe.")
        if not server.startswith(("http://", "https://")):
            raise PublishApiError("Ingresá la URL del servidor (http://...).")
        if not api_key:
            raise PublishApiError("Ingresá la API key.")
        return client_dir, PublishApi(server, api_key)

    def start_compare(self):
        self.btn_compare.configure(state="disabled")
        self.btn_publish.configure(state="disabled")
        self.publish_plan = None
        threading.Thread(target=self._compare_worker, daemon=True).start()

    def _compare_worker(self):
        try:
            client_dir, api = self.publish_inputs()
            mirror = self.publish_mode.get() == "mirror"
            exclude_dirs, exclude_files = self.active_exclusions()

            local = scan_client(
                client_dir, exclude_dirs, exclude_files,
                on_progress=lambda i, total, rel: self.update_publish_status(
                    f"Escaneando ({i}/{total}): {rel}", i / total * 0.9
                ),
            )
            self.update_publish_status("Consultando el servidor...", 0.95)
            remote = api.get_state()
            plan = diff_plan(local, remote, mirror, exclude_dirs, exclude_files)

            launcher_changed = False
            if self.include_launcher.get():
                local_launcher = os.path.join(client_dir, LAUNCHER_EXE)
                if os.path.isfile(local_launcher):
                    remote_launcher = next(
                        (f for f in remote if f["path"].casefold() == LAUNCHER_EXE), None
                    )
                    launcher_changed = (remote_launcher is None or
                                        remote_launcher["sha256"] != sha256_file(local_launcher))

            self.after(0, self._show_plan, client_dir, local, plan, launcher_changed)
        except (PublishApiError, OSError) as e:
            self.update_publish_status(f"❌ {e}", 0)
        finally:
            self.after(0, lambda: self.btn_compare.configure(state="normal"))

    def _show_plan(self, client_dir, local, plan, launcher_changed):
        uploads = len(plan["new"]) + len(plan["modified"]) + (1 if launcher_changed else 0)
        self.lbl_publish_summary.configure(
            text=(f"Nuevos: {len(plan['new'])} · Modificados: {len(plan['modified'])}"
                  f" · A borrar: {len(plan['delete'])} · Sin cambios: {plan['unchanged']}"
                  + (" · launcher.exe cambió" if launcher_changed else ""))
        )
        lines = ([f"+ {p}" for p in plan["new"]] + [f"~ {p}" for p in plan["modified"]]
                 + ([f"~ {LAUNCHER_EXE}"] if launcher_changed else [])
                 + [f"- {p}" for p in plan["delete"]])
        self.txt_publish_changes.configure(state="normal")
        self.txt_publish_changes.delete("1.0", "end")
        self.txt_publish_changes.insert("1.0", "\n".join(lines) or "No hay diferencias.")
        self.txt_publish_changes.configure(state="disabled")

        self.publish_plan = {
            "client_dir": client_dir,
            "local": local,
            "plan": plan,
            "launcher_changed": launcher_changed,
        }
        # Aunque no haya archivos para subir, publicar sirve para actualizar el manifest.
        self.btn_publish.configure(state="normal")
        self.update_publish_status(
            f"Listo: {uploads} archivo(s) para subir y {len(plan['delete'])} para borrar.", 1.0
        )

    def start_publish(self):
        prepared = self.publish_plan
        if prepared is None:
            return
        to_delete = prepared["plan"]["delete"]
        if to_delete:
            preview = "\n".join(to_delete[:10])
            more = f"\n… y {len(to_delete) - 10} más" if len(to_delete) > 10 else ""
            ok = messagebox.askyesno(
                "Confirmar borrado",
                f"Se van a BORRAR {len(to_delete)} archivo(s) del servidor:\n\n{preview}{more}"
                "\n\n¿Continuar?",
            )
            if not ok:
                return
        if is_insecure_url(self.entry_server_url.get().strip()):
            ok = messagebox.askyesno(
                "Conexión sin cifrar",
                "El servidor usa http://: la API key viaja sin cifrar y alguien en la "
                "misma red podría leerla.\n\nUsá https:// cuando el servidor lo tenga."
                "\n\n¿Publicar igual?",
                icon="warning",
            )
            if not ok:
                return
        self.run_publish(prepared, force=False)

    def run_publish(self, prepared, force):
        self.btn_publish.configure(state="disabled")
        self.btn_compare.configure(state="disabled")
        threading.Thread(target=self._publish_worker, args=(prepared, force),
                         daemon=True).start()

    def _ask_discard_other_session(self, prepared, error):
        ok = messagebox.askyesno(
            "Publicación en curso",
            f"{error}.\n\nPuede ser de otra ventana de la tool, de otra persona, o un "
            "intento anterior que se cortó.\n\n¿Descartarla y publicar igual?",
            icon="warning",
        )
        if ok:
            self.run_publish(prepared, force=True)
        else:
            self.update_publish_status("Publicación cancelada: hay otra en curso.", 0)
            self.btn_publish.configure(state="normal")

    def _publish_worker(self, prepared, force=False):
        session_id = None
        api = None
        try:
            client_dir, api = self.publish_inputs()
            plan = prepared["plan"]
            local_by_path = {f["path"]: f for f in prepared["local"]}
            uploads = [local_by_path[p] for p in plan["new"] + plan["modified"]]
            extra_files = []
            if prepared["launcher_changed"]:
                launcher_path = os.path.join(client_dir, LAUNCHER_EXE)
                uploads.append({"path": LAUNCHER_EXE, "sha256": sha256_file(launcher_path)})
                extra_files.append(LAUNCHER_EXE)

            try:
                session_id = api.create_session(force=force)
            except PublishApiError as e:
                if e.status == 409 and not force:
                    self.after(0, self._ask_discard_other_session, prepared, e)
                    self.update_publish_status("Hay otra publicación en curso.", 0)
                    return
                raise
            total = len(uploads)
            for i, item in enumerate(uploads):
                self.update_publish_status(
                    f"Subiendo ({i + 1}/{total}): {item['path']}", i / max(total, 1) * 0.95
                )
                full_path = os.path.join(client_dir, *item["path"].split("/"))
                api.upload_file(session_id, item["path"], full_path, item["sha256"])

            self.update_publish_status("Publicando...", 0.97)
            version = self.entry_publish_ver.get().strip() or "1.0.0"
            result = api.publish(session_id, build_manifest(prepared["local"], version),
                                 plan["delete"], extra_files)
            session_id = None
            self.publish_plan = None
            self.update_publish_status(
                f"✅ Publicado: {result['uploaded']} subidos, {len(result['deleted'])} borrados,"
                f" manifest con {result['manifestFiles']} archivos.", 1.0
            )
        except (PublishApiError, OSError) as e:
            self.update_publish_status(f"❌ {e}", 0)
            self.after(0, lambda: self.btn_publish.configure(state="normal"))
        finally:
            if session_id and api:
                try:
                    api.cancel_session(session_id)
                except PublishApiError:
                    pass
            self.after(0, lambda: self.btn_compare.configure(state="normal"))

    def update_publish_status(self, text, progress=None):
        def _update():
            self.lbl_publish_status.configure(text=text)
            if progress is not None:
                self.progress_publish.set(progress)
        self.after(0, _update)


if __name__ == "__main__":
    app = ClientToolsApp()
    app.mainloop()
