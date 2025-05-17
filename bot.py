import sys
import time
import logging
from config import Config
from managers.browser_manager import BrowserManager
from managers.session_manager import SessionManager
from whatsapp_client import WhatsAppClient
from llm_provider import LLMProviderFactory
from managers.chat_manager import ChatManager
from managers.prompt_manager import PromptManager
from processors.response_processor import ResponseProcessor
from processors.message_processor import MessageProcessor
from managers.chat_persistence_manager import ChatPersistenceManager

logger = logging.getLogger(__name__)


class WhatsAppBot:
    def __init__(self):
        # Inicializar configuración
        self.config = Config()

        # Inicializar componentes
        self.browser_manager = BrowserManager(self.config)

        # Inicializar navegador
        if not self.browser_manager.initialize_browser():
            logger.error("No se pudo inicializar el navegador. Saliendo...")
            sys.exit(1)

        # Obtener driver
        self.driver = self.browser_manager.driver

        # Inicializar otros componentes
        self.session_manager = SessionManager(self.config, self.driver)
        self.whatsapp_client = WhatsAppClient(self.driver, self.config)

        # Inicializar administrador de chats y prompts
        self.chat_persistence_manager = ChatPersistenceManager(self.config)
        self.chat_manager = ChatManager(self.config, self.chat_persistence_manager)
        self.prompt_manager = PromptManager(self.config)

        # Inicializar procesador de respuestas
        self.response_processor = ResponseProcessor()

        # Inicializar proveedor LLM
        llm_type = self.config.config.get("llm", {}).get("default", "gemini")
        self.llm_provider = LLMProviderFactory.create_provider(llm_type, self.config)

        if not self.llm_provider:
            logger.error(
                f"No se pudo inicializar el proveedor LLM: {llm_type}. Saliendo..."
            )
            sys.exit(1)

        # Inicializar procesador de mensajes
        self.message_processor = MessageProcessor(
            self.whatsapp_client,
            self.chat_manager,
            self.prompt_manager,
            self.llm_provider,
            self.response_processor,
        )

    def run(self):
        """Ejecutar el bot"""
        try:
            # Iniciar sesión en WhatsApp
            if not self.whatsapp_client.login(self.session_manager):
                logger.error("Error al iniciar sesión en WhatsApp. Saliendo...")
                return

            logger.info("Bot iniciado correctamente")

            # Intervalo de verificación de mensajes
            check_interval = self.config.config.get("chat", {}).get(
                "check_interval", 10
            )

            while True:
                self.message_processor.process_unread_chats()
                time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("Bot detenido por el usuario")
        except Exception as e:
            logger.error(f"Error inesperado: {e}", exc_info=True)
        finally:
            # Guardar sesión y cerrar navegador
            self.session_manager.save_session()
            self.browser_manager.close()


if __name__ == "__main__":
    bot = WhatsAppBot()
    bot.run()
