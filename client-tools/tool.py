import os
import sys
import json
import hashlib
import threading
import base64
from pathlib import Path
from tkinter import filedialog

# Permite ejecutar este archivo directamente desde client-tools o desde otra carpeta.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
        self.geometry("560x700")
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

        self.setup_manifest_tab()
        self.setup_patcher_tab()

    def _set_icon(self):
        try:
            icon_path = Path.cwd() / "data" / "temp" / "client_tools_icon.ico"
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
            "Launcher": ctk.BooleanVar(value=True),
            ".git": ctk.BooleanVar(value=True),
            "__pycache__": ctk.BooleanVar(value=True),
        }
        self.exclude_files = {
            "manifest.json": ctk.BooleanVar(value=True),
            "manifest.py": ctk.BooleanVar(value=True),
            "tool.py": ctk.BooleanVar(value=True),
            "tool.exe": ctk.BooleanVar(value=True),
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

        exclude_dirs = {
            name.casefold() for name, variable in self.exclude_dirs.items() if variable.get()
        }
        exclude_files = {
            name.casefold() for name, variable in self.exclude_files.items() if variable.get()
        }

        files_manifest = []
        all_files = []

        for root, dirs, files in os.walk(client_dir):
            dirs[:] = [d for d in dirs if d.casefold() not in exclude_dirs]
            for f in files:
                if f.casefold() not in exclude_files:
                    all_files.append(os.path.join(root, f))

        total_files = len(all_files)
        if total_files == 0:
            self.update_manifest_status("No se encontraron archivos para incluir.", 0)
            self.btn_gen_manifest.configure(state="normal")
            return

        def calcular_sha256(path):
            sha256 = hashlib.sha256()
            with open(path, "rb") as f:
                for bloque in iter(lambda: f.read(8192), b""):
                    sha256.update(bloque)
            return sha256.hexdigest()

        for i, full_path in enumerate(all_files):
            try:
                rel_path = os.path.relpath(full_path, client_dir).replace("\\", "/")
                size = os.path.getsize(full_path)
                sha256 = calcular_sha256(full_path)

                files_manifest.append({
                    "path": rel_path,
                    "size": size,
                    "sha256": sha256
                })

                prog = (i + 1) / total_files
                self.update_manifest_status(f"Procesando ({i+1}/{total_files}): {rel_path}", prog)
            except Exception as e:
                print(f"Error procesando {full_path}: {e}")

        manifest = {
            "version": manifest_version,
            "file_count": len(files_manifest),
            "files": files_manifest
        }

        output_path = os.path.join(client_dir, "manifest.json")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            self.update_manifest_status(f"✅ ¡Manifest generado con éxito ({len(files_manifest)} archivos)!", 1.0)
        except Exception as e:
            self.update_manifest_status(f"Error guardando manifest.json: {e}", 0)
        finally:
            self.btn_gen_manifest.configure(state="normal")

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


if __name__ == "__main__":
    app = ClientToolsApp()
    app.mainloop()
