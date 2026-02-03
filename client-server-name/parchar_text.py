import sys

def patch_3byte_xor(filename, old_str, new_str):
    print(f"Abriendo {filename}...")
    try:
        with open(filename, 'rb') as f:
            data = bytearray(f.read())
    except FileNotFoundError:
        print("ERROR: No se encuentra el archivo. Asegurate que Text_Eng.bmd este en la misma carpeta.")
        return

    # La llave exacta que descubrí en tu archivo
    KEY = [0xFC, 0xCF, 0xAB]
    
    # Preparamos el patrón de búsqueda encriptado
    # El patrón depende de la posición (alineación de 3 bytes), así que buscaremos inteligentemente.
    print(f"Buscando '{old_str}' encriptado...")
    
    found_count = 0
    
    # Recorremos el archivo buscando el patrón
    # Buscamos coincidencias basadas en la lógica de desencriptado
    i = 0
    while i < len(data) - len(old_str):
        match = True
        # Verificamos si los siguientes bytes coinciden con "SSeMU" al desencriptarlos
        for j in range(len(old_str)):
            # Byte desencriptado = ByteArchivo ^ Key[(Posición) % 3]
            decrypted_char = data[i+j] ^ KEY[(i+j) % 3]
            if chr(decrypted_char) != old_str[j]:
                match = False
                break
        
        if match:
            found_count += 1
            # ¡Encontrado! Ahora sobrescribimos
            print(f" -> Encontrado en offset {i}. Reemplazando...")
            
            # 1. Escribir el Nuevo Nombre
            for j in range(len(new_str)):
                # Encriptamos el nuevo caracter: NuevoByte ^ Key
                encrypted_char = ord(new_str[j]) ^ KEY[(i+j) % 3]
                data[i+j] = encrypted_char
                
            # 2. Rellenar con ceros (null bytes) si el nuevo nombre es más corto
            # Esto borra las letras sobrantes del nombre viejo
            padding_len = len(old_str) - len(new_str)
            for j in range(padding_len):
                pos = i + len(new_str) + j
                # 0x00 ^ Key = Key
                data[pos] = 0x00 ^ KEY[pos % 3]
                
            # Saltamos estos bytes para no volver a encontrarlos
            i += len(old_str)
        else:
            i += 1

    if found_count > 0:
        print(f"\n¡ÉXITO! Se reemplazaron {found_count} ocurrencias.")
        new_filename = "Text_Eng_Fixed.bmd"
        with open(new_filename, 'wb') as f:
            f.write(data)
        print(f"Archivo guardado como: {new_filename}")
        print("Renómbralo a Text_Eng.bmd y ponlo en tu cliente.")
    else:
        print("\nERROR: No se encontró el texto. Verifica que escribiste 'SSeMU' exactamente igual (mayúsculas/minúsculas).")

# EJECUTAR
# Cambia "Angel" por el nombre que quieras. Max 5 letras si reemplazas SSeMU.
# Si quieres poner un nombre largo, avísame, porque SSeMU es corto.
patch_3byte_xor("Text_Eng.bmd", "SSeMU", "Mu Campana")