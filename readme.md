pyinstaller --noconfirm --onefile --windowed --uac-admin --icon=icon.ico launcher.py

pyinstaller --noconfirm --onefile --windowed --uac-admin --manifest "app.manifest" --version-file "file_version_info.txt" --icon=icon.ico launcher.py

pyinstaller --noconfirm --onefile --windowed --uac-admin --icon=icon.ico updater/updater.py

pyinstaller --noconfirm --onefile --windowed --icon=icon.ico client-tools/tool.py


# 🚀 Mu Launcher & Client Tools

Este repositorio contiene el sistema completo del **Launcher**, **Updater** (auto-actualizador gráfico) y **Client Tools** (herramienta unificada de administración del cliente).

---

## 📦 Compilación de Ejecutables (.exe)

### 🔹 Launcher (`launcher.exe`)
```bash
pyinstaller --noconfirm --onefile --windowed --uac-admin --icon=icon.ico launcher.py
```
```bash
pyinstaller --noconfirm --onefile --windowed --uac-admin --manifest "app.manifest" --version-file "file_version_info.txt" --icon=icon.ico launcher.py
```

### 🔹 Updater (`updater.exe`)
```bash
pyinstaller --noconfirm --onefile --windowed --uac-admin --icon=icon.ico updater/updater.py
```

### 🔹 Client Tools (`tool.exe`)
```bash
pyinstaller --noconfirm --onefile --windowed --icon=icon.ico client-tools/tool.py
```

---

## 🛠️ Descripción y Uso de los Componentes

### 🖥️ 1. Launcher (`launcher.exe`)
* **Ubicación**: Raíz de la carpeta del cliente de juego.
* **Comportamiento**:
  * **Verificación al inicio**: Comprueba automáticamente en el servidor si existe una nueva versión de `launcher.exe`. Si la hay, la descarga a `data/temp/new_launcher.exe` y ejecuta el `updater.exe`.
  * **Configuración del cliente**: Permite seleccionar resolución, modo ventana, sonido/música, volumen e idioma (`Spn`, `Eng`, `Por`).
  * **Actualizador de archivos de juego**: Al presionar "Verificar y Actualizar", descarga los archivos del cliente que falten o cuyo SHA256 no coincida con el servidor.
  * **Lanzamiento**: Guarda las preferencias en el Registro de Windows (`HKCU\Software\Webzen\MU\config`) e inicia `main.exe`.

### 🔄 2. Updater (`updater.exe`)
* **Ubicación**: Misma carpeta raíz que `launcher.exe`.
* **Comportamiento**: Muestra una ventana con barra de progreso y estado. Recibe por parámetros la ruta del ejecutable descargado y el PID del launcher. Espera a que el launcher se cierre, sustituye `launcher.exe` de forma segura y vuelve a abrir el launcher actualizado.

### 🛠️ 3. Client Tools (`client-tools/tool.py` / `tool.exe`)
Herramienta con interfaz gráfica Tkinter / CustomTkinter compuesta por 2 pestañas:
1. **Generador Manifest**: Selecciona la carpeta del cliente, calcula tamaño y SHA256 de cada archivo (omitiendo temporales y desarrollos) y crea `manifest.json`.
2. **Parchador de Servidor**: Busca y reemplaza encriptando/desencriptando por algoritmo XOR el nombre del servidor (ej. de `SSeMU` a `Mu Campana`) en los archivos `Text_Eng.bmd`, `Text_Spn.bmd` y `Text_Por.bmd`.