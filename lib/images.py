from PIL import Image
import os
import io


def convertir_a_png_y_reducir(imagen_origen, ruta_salida):
    # Cargar la imagen
    img = Image.open(imagen_origen)

    # Convertir a PNG
    img = img.convert('RGBA')

    # Comprimir imagen hasta un peso menor a 2MB
    max_size = 2 * 1024 * 1024  # Tamaño máximo en bytes
    factor_calidad = 99  # Iniciamos con alta calidad

    while True:
        buf = io.BytesIO()
        img.save(buf, format='PNG', quality=factor_calidad)
        size = buf.tell()

        if size < max_size or factor_calidad < 0:
            break

        # Reducir la calidad
        factor_calidad -= 10

    # Guardar la imagen
    with open(ruta_salida, 'wb') as f:
        f.write(buf.getvalue())

    print(f"Imagen guardada en {ruta_salida} con un tamaño de {size / 1024} KB")
