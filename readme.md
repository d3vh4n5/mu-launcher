pyinstaller --noconfirm --onefile --windowed --uac-admin --icon=icon.ico launcher.py

pyinstaller --noconfirm --onefile --windowed --uac-admin --manifest "app.manifest" --version-file "file_version_info.txt" --icon=icon.ico launcher.py