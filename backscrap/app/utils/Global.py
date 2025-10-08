from backscrap.app.pojo.models.modelos import CustomResponse
import cv2
import os
from datetime import datetime
from backscrap.app.utils.config import DEV_MODE

class ResponseUtil:
    
    @staticmethod
    def success(message="Operación realizada con éxito.", data=None) -> CustomResponse:
        return CustomResponse(status=2, message=message, data=data or {})
    
    @staticmethod
    def error(message="Ocurrió un error.", data=None) -> CustomResponse:
        return CustomResponse(status=4, message=message, data=data or {})
    
    @staticmethod
    def warning(message="Usuario no registrado.", data=None) -> CustomResponse:
        return CustomResponse(status=3, message=message, data=data or {})


class Console:
    
    dev_mode = DEV_MODE
    
    @staticmethod
    def isDevMode():
        # Define si estás en modo de desarrollo o no
        return Console.dev_mode  # Cambia a False para deshabilitar mensajes en producción

    @staticmethod
    def set_dev_mode(value: bool):
        Console.dev_mode = value

    @staticmethod
    def log(*msg):
        if Console.isDevMode():
            print(*msg)

    @staticmethod
    def table(data):
        if Console.isDevMode():
            if isinstance(data, (list, dict)):
                from pprint import pprint  # pretty-print para estructuras complejas
                pprint(data)
            else:
                print(data)

    @staticmethod
    def warn(*msg):
        if Console.isDevMode():
            print(f"WARNING: {' '.join(map(str, msg))}")

    @staticmethod
    def error(*msg):
        if Console.isDevMode():
            print(f"ERROR: {' '.join(map(str, msg))}")

    @staticmethod
    def saveImg(folder, face):
        if Console.isDevMode():
            output_dir = os.path.join(os.getcwd(), "assets", folder)
            os.makedirs(output_dir, exist_ok=True)  # Crear el directorio si no existe

            # Construir el nombre del archivo
            file_name = f"face_{datetime.now().microsecond}.jpg"
            file_path = os.path.join(output_dir, file_name)

            # Guardar la imagen
            cv2.imwrite(file_path, face)

            print(f"Imagen guardada en: {file_path}")