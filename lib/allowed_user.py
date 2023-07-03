import json

# Carga los IDs de usuario permitidos desde un archivo JSON
#with open('allowed_user_ids.json', 'r') as f:
#    ALLOWED_USER_IDS = json.load(f)

def is_user_allowed(update):
    # Obtiene el ID de usuario del mensaje
    user_id = update.message.from_user.id

    # Uso de la función para cargar los IDs de usuario permitidos
    ALLOWED_USER_IDS = load_allowed_user_ids()

    # Comprueba si el ID de usuario está en la lista de ID permitidos
    if user_id in ALLOWED_USER_IDS:
        return True
    else:
        return False
#No usar directamente estas funciones
def load_allowed_user_ids(filename='allowed_user_ids.json'):
    try:
        with open(filename, 'r') as f:
            allowed_user_ids = json.load(f)
        return allowed_user_ids
    except FileNotFoundError:
        print(f"Archivo {filename} no encontrado.")
        return []
    except json.JSONDecodeError:
        print(f"Error al leer el archivo {filename}. Asegúrate de que tenga un formato JSON válido.")
        return []
    except Exception as e:
        print(f"Error al cargar los IDs de usuario permitidos: {e}")
        return []
