import os
import json
import logging
from dotenv import load_dotenv


class Config:
    def __init__(self, config_file_path="config.json"):
        # Cargar variables de entorno
        load_dotenv()

        # Rutas y directorios
        self.abs_path = os.path.dirname(os.path.abspath(__file__))
        self.browser_data_path = os.path.join(self.abs_path, "browser_data")
        self.session_path = os.path.join(self.abs_path, "whatsapp_session.pkl")
        self.logs_path = os.path.join(self.abs_path, "logs")

        # Crear directorios necesarios
        os.makedirs(self.browser_data_path, exist_ok=True)
        os.makedirs(self.logs_path, exist_ok=True)

        # Configurar logging
        self.setup_logging()

        # Cargar configuración desde archivo JSON
        self.config = self.load_config(config_file_path)

        # Obtener API keys desde variables de entorno
        self.llm_api_keys = {
            "gemini": os.getenv("GEMINI_API_KEY"),
            # Agregar otras API keys según sea necesario
        }

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(os.path.join(self.logs_path, "bot.log")), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self, config_file_path):
        try:
            if os.path.exists(config_file_path):
                with open(config_file_path, "r", encoding="utf-8") as file:
                    return json.load(file)
            else:
                # Configuración por defecto
                default_config = {
                    "browser": {"headless": False, "window_size": "1366,768"},
                    "chat": {"max_history": 20, "check_interval": 10},
                    "llm": {
                        "default": "gemini",
                        "prompt_template_path": "prompts/default_template.txt",
                    },
                }
                # Guardar configuración por defecto
                with open(config_file_path, "w", encoding="utf-8") as file:
                    json.dump(default_config, file, indent=4)
                return default_config
        except Exception as e:
            self.logger.error(f"Error al cargar configuración: {e}", exc_info=True)
            return {}
