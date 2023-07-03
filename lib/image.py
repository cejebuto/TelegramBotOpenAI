from PIL import Image
import os
import time

def convert_to_png_and_reduce(photo_file):
    try:
        # Descargar la foto a un directorio temporal
        file_path = "temp/{}.jpg".format(time.strftime("%Y%m%d%H%M%S"))
        photo_file.download(file_path)

        # Abrir la imagen con PIL, esto debería funcionar independientemente del formato de la imagen
        image = Image.open(file_path)

        # Convertir a JPEG si la imagen no es JPEG
        if image.format != 'JPEG':
            jpg_file_path = "temp/{}.jpg".format(time.strftime("%Y%m%d%H%M%S"))
            image.convert('RGB').save(jpg_file_path, 'JPEG')
            image = Image.open(jpg_file_path)
            os.remove(file_path)  # Eliminar el archivo original
            file_path = jpg_file_path

        # Reducir el tamaño de la imagen si es mayor que 2MB
        if os.path.getsize(file_path) > 2 * 1024 * 1024:
            # Redimensionar la imagen para que tenga un ancho máximo de 1024 píxeles
            max_width = 1024
            width, height = image.size
            if width > max_width:
                new_width = max_width
                new_height = int((float(height) / width) * new_width)
                image = image.resize((new_width, new_height))

            # Guardar la imagen reducida como JPEG
            reduced_file_path = "temp/{}_reduced.jpg".format(time.strftime("%Y%m%d%H%M%S"))
            image.save(reduced_file_path, 'JPEG')
            os.remove(file_path)  # Eliminar el archivo original
            file_path = reduced_file_path

        # Convertir y guardar la imagen en formato PNG
        png_file_path = "temp/{}.png".format(time.strftime("%Y%m%d%H%M%S"))
        image = Image.open(file_path)
        image.save(png_file_path, "PNG")
        os.remove(file_path)  # Eliminar el archivo JPEG reducido si existe

        # Comprobar si el tamaño del archivo PNG es mayor que 2MB
        if os.path.getsize(png_file_path) > 2 * 1024 * 1024:
            print("La imagen es demasiado grande y no puede ser reducida a menos de 2MB usando PIL.")
            return False

        return png_file_path

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return False


def print_image_info(image_path):
    try:
        # Abrir la imagen con PIL
        image = Image.open(image_path)

        # Obtener el formato de la imagen
        image_format = image.format

        # Obtener la resolución de la imagen
        width, height = image.size
        resolution = f"{width}x{height}"

        # Obtener el peso de la imagen en MB
        image_size = os.path.getsize(image_path) / (1024 * 1024)  # Convertir a MB

        # Obtener la ruta y el nombre de archivo
        image_dir, image_filename = os.path.split(image_path)

        # Imprimir la información de la imagen
        print(f"Ruta: {image_dir}")
        print(f"Nombre: {image_filename}")
        print(f"Formato: {image_format}")
        print(f"Resolución: {resolution}")
        print(f"Peso: {image_size:.2f} MB")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

