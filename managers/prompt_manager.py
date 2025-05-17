import os
import time
import logging

logger = logging.getLogger(__name__)


class PromptManager:
    def __init__(self, config):
        self.config = config
        self.template_path = os.path.join(
            config.abs_path,
            config.config.get("llm", {}).get(
                "prompt_template_path", "prompts/default_template.txt"
            ),
        )
        self._ensure_template_exists()

    def _ensure_template_exists(self):
        """Asegura que exista el archivo de plantilla de prompt"""
        try:
            os.makedirs(os.path.dirname(self.template_path), exist_ok=True)

            if not os.path.exists(self.template_path):
                default_template = """
                <VirtualAssistant>
                    <Role>
                        <Name>Luna</Name>
                        <Description>Asistente virtual que gestiona los mensajes de WhatsApp.</Description>
                    </Role>
                    <UserInformation>
                        <Name>{chat_name}</Name>
                        <PreviousInteractions>{chat_history}</PreviousInteractions>
                    </UserInformation>
                </VirtualAssistant>
                """

                with open(self.template_path, "w", encoding="utf-8") as file:
                    file.write(default_template.strip())
                logger.info(f"Plantilla de prompt creada en: {self.template_path}")
        except Exception as e:
            logger.error(f"Error al crear plantilla de prompt: {e}", exc_info=True)

    def load_template(self):
        """Cargar la plantilla del prompt desde el archivo"""
        try:
            with open(self.template_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error al cargar plantilla de prompt: {e}", exc_info=True)
            # Devolver una plantilla básica en caso de error
            return "Eres un asistente de WhatsApp. Proporciona una respuesta breve y útil al mensaje: {chat_history}"

    def format_prompt(self, chat_name, messages):
        """Formatear el prompt con los datos del chat"""
        template = self.load_template()
        chat_history = "\n".join(
            f"<Message sender={msg['sender']} date={msg['date']} time={msg['time']}>{msg['message']}</Message>"
            for msg in messages
        )

        current_datetime = time.strftime("%Y-%m-%d:%H-%M-%S:%Z")
        return template.format(chat_name=chat_name, chat_history=chat_history, current_datetime=current_datetime)
