import os
import sys
import json
import hashlib
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

# Colores de la app
primary_color = "#1f538d"
primary_color_light = "#2980b9"
bg_color = "#0f0f0f"

class ClientToolsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("Herramientas de Cliente MU")
        self.geometry("520x480")
        self.resizable(False, False)
        self.configure(fg_color=bg_color)

        # Tabview para las 2 herramientas
        self.tabview = ctk.CTkTabview(self, width=490, height=440)
        self.tabview.pack(padx=15, pady=10, fill="both", expand=True)

        self.tab_manifest = self.tabview.add("Generador Manifest")
        self.tab_patcher = self.tabview.add("Parchador de Servidor")

        self.setup_manifest_tab()
        self.setup_patcher_tab()

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

        self.entry_client_dir = ctk.CTkEntry(frame_dir, width=350)
        self.entry_client_dir.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_client_dir.insert(0, os.getcwd())

        btn_browse_dir = ctk.CTkButton(
            frame_dir, text="Examinar", width=80, command=self.browse_client_dir
        )
        btn_browse_dir.pack(side="right")

        # Versión manifest
        frame_version = ctk.CTkFrame(tab, fg_color="transparent")
        frame_version.pack(fill="x", padx=10, pady=5)

        lbl_ver = ctk.CTkLabel(frame_version, text="Versión Manifest:", font=("Arial", 11))
        lbl_ver.pack(side="left", padx=(0, 10))

        self.entry_manifest_ver = ctk.CTkEntry(frame_version, width=100)
        self.entry_manifest_ver.pack(side="left")
        self.entry_manifest_ver.insert(0, "1.0.0")

        # Progreso y Estado
        self.lbl_manifest_status = ctk.CTkLabel(
            tab, text="Listo para generar manifest.json", text_color="#adadad"
        )
        self.lbl_manifest_status.pack(padx=10, pady=(10, 2))

        self.progress_manifest = ctk.CTkProgressBar(tab, width=440, progress_color=primary_color)
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

    def _generate_manifest_worker(self):
        client_dir = self.entry_client_dir.get().strip()
        manifest_version = self.entry_manifest_ver.get().strip() or "1.0.0"

        if not os.path.isdir(client_dir):
            self.update_manifest_status("Error: Directorio del cliente no válido.", 0)
            return

        self.btn_gen_manifest.configure(state="disabled")
        self.update_manifest_status("Escaneando archivos...", 0.1)

        exclude_dirs = {"Logs", "ScreenShots", "Temp", "Launcher", ".git", "__pycache__"}
        exclude_files = {"manifest.json", "manifest.py", "tool.exe"}

        files_manifest = []
        all_files = []

        for root, dirs, files in os.walk(client_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                if f not in exclude_files:
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
            font=("Arial", 11), text_color="#adadad"
        )
        lbl_info.pack(anchor="w", padx=10, pady=(10, 5))

        # Texto a buscar (Viejo)
        lbl_old = ctk.CTkLabel(tab, text="Texto original a buscar:", font=("Arial", 12, "bold"))
        lbl_old.pack(anchor="w", padx=10, pady=(5, 2))

        self.entry_old_str = ctk.CTkEntry(tab, width=440)
        self.entry_old_str.pack(padx=10, pady=2)
        self.entry_old_str.insert(0, "SSeMU")

        # Texto a poner (Nuevo)
        lbl_new = ctk.CTkLabel(tab, text="Nuevo nombre del servidor:", font=("Arial", 12, "bold"))
        lbl_new.pack(anchor="w", padx=10, pady=(10, 2))

        self.entry_new_str = ctk.CTkEntry(tab, width=440)
        self.entry_new_str.pack(padx=10, pady=2)
        self.entry_new_str.insert(0, "Mu Campana")

        # Archivos objetivo
        lbl_target = ctk.CTkLabel(tab, text="Carpeta de archivos BMD:", font=("Arial", 12, "bold"))
        lbl_target.pack(anchor="w", padx=10, pady=(10, 2))

        frame_bmd = ctk.CTkFrame(tab, fg_color="transparent")
        frame_bmd.pack(fill="x", padx=10, pady=2)

        self.entry_bmd_dir = ctk.CTkEntry(frame_bmd, width=350)
        self.entry_bmd_dir.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_bmd_dir.insert(0, os.getcwd())

        btn_browse_bmd = ctk.CTkButton(
            frame_bmd, text="Examinar", width=80, command=self.browse_bmd_dir
        )
        btn_browse_bmd.pack(side="right")

        # Estado del parcheador
        self.lbl_patcher_status = ctk.CTkLabel(
            tab, text="Listo para aplicar parche.", text_color="#adadad"
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
