import logging

logger = logging.getLogger(__name__)


class ChatManager:
    def __init__(self, config, persistence_manager=None):
        self.config = config
        self.max_history = config.config.get("chat", {}).get("max_history", 20)
        self.chat_history = {}
        self.persistence_manager = persistence_manager

        # Cargar historiales existentes si hay un gestor de persistencia
        if self.persistence_manager:
            self._load_existing_chats()

    def _load_existing_chats(self):
        """Cargar historiales existentes desde archivos"""
        available_chats = self.persistence_manager.list_available_chats()
        for chat_name in available_chats:
            messages = self.persistence_manager.load_chat_history(chat_name)
            # Asegurarse de respetar el máximo de mensajes configurado
            if len(messages) > self.max_history:
                messages = messages[-self.max_history :]
            self.chat_history[chat_name] = messages
            logger.debug(
                f"Historial cargado para chat: {chat_name}, {len(messages)} mensajes"
            )

    def add_messages(self, chat_name, messages):
        """Añadir mensajes al historial de un chat"""
        if not isinstance(messages, list):
            messages = [messages]

        if chat_name not in self.chat_history:
            self.chat_history[chat_name] = []

        # Agregar nuevos mensajes al historial
        self.chat_history[chat_name].extend(messages)

        # Limitar el historial al número máximo configurado
        if len(self.chat_history[chat_name]) > self.max_history:
            self.chat_history[chat_name] = self.chat_history[chat_name][
                -self.max_history :
            ]

        # Persistir los cambios si hay un gestor de persistencia
        if self.persistence_manager:
            self.persistence_manager.save_chat_history(
                chat_name, self.chat_history[chat_name]
            )

    def get_chat_history(self, chat_name):
        """Obtener el historial de un chat"""
        # Si no está en memoria y hay un gestor de persistencia, intentar cargarlo
        if chat_name not in self.chat_history and self.persistence_manager:
            messages = self.persistence_manager.load_chat_history(chat_name)
            if messages:
                self.chat_history[chat_name] = messages

        return self.chat_history.get(chat_name, [])

    def clear_chat_history(self, chat_name=None):
        """Limpiar el historial de un chat o de todos los chats"""
        if chat_name:
            if chat_name in self.chat_history:
                self.chat_history[chat_name] = []
                # Eliminar también de persistencia
                if self.persistence_manager:
                    self.persistence_manager.delete_chat_history(chat_name)
        else:
            self.chat_history = {}
            # Eliminar todos los historiales persistentes
            if self.persistence_manager:
                self.persistence_manager.delete_chat_history()
