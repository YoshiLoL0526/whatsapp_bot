import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatPersistenceManager:
    def __init__(self, config):
        self.config = config
        # Obtener la ruta donde se guardarán los archivos JSON
        self.storage_path = config.config.get("chat", {}).get(
            "storage_path", "chat_history"
        )

        # Crear el directorio si no existe
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            logger.info(f"Directorio de almacenamiento creado: {self.storage_path}")

    def save_chat_history(self, chat_name, messages):
        """Guardar el historial de chat en un archivo JSON"""
        try:
            # Validar formato de mensajes
            for msg in messages:
                if (
                    not isinstance(msg, dict)
                    or "sender" not in msg
                    or "message" not in msg
                ):
                    raise ValueError(
                        "Formato de mensaje inválido. Se requiere {'sender': str, 'message': str}"
                    )

            file_path = os.path.join(self.storage_path, f"{chat_name}.json")
            data = {"last_updated": datetime.now().isoformat(), "messages": messages}

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Historial guardado para chat '{chat_name}'")
            return True
        except Exception as e:
            logger.error(
                f"Error al guardar historial para chat '{chat_name}': {str(e)}"
            )
            return False

    def load_chat_history(self, chat_name):
        """Cargar el historial de chat desde un archivo JSON"""
        file_path = os.path.join(self.storage_path, f"{chat_name}.json")

        if not os.path.exists(file_path):
            logger.debug(f"No existe historial previo para chat '{chat_name}'")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.debug(f"Historial cargado para chat '{chat_name}'")
            return data.get("messages", [])
        except Exception as e:
            logger.error(f"Error al cargar historial para chat '{chat_name}': {str(e)}")
            return []

    def delete_chat_history(self, chat_name=None):
        """Eliminar el archivo de historial de un chat o de todos los chats"""
        if chat_name:
            file_path = os.path.join(self.storage_path, f"{chat_name}.json")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Historial eliminado para chat '{chat_name}'")
                except Exception as e:
                    logger.error(
                        f"Error al eliminar historial para chat '{chat_name}': {str(e)}"
                    )
        else:
            try:
                # Eliminar todos los archivos JSON en el directorio
                for filename in os.listdir(self.storage_path):
                    if filename.endswith(".json"):
                        os.remove(os.path.join(self.storage_path, filename))
                logger.info("Todos los historiales de chat han sido eliminados")
            except Exception as e:
                logger.error(f"Error al eliminar todos los historiales: {str(e)}")

    def list_available_chats(self):
        """Listar todos los chats disponibles"""
        try:
            chat_files = [
                f[:-5] for f in os.listdir(self.storage_path) if f.endswith(".json")
            ]
            return chat_files
        except Exception as e:
            logger.error(f"Error al listar chats disponibles: {str(e)}")
            return []
