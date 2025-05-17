import logging
from abc import ABC, abstractmethod
import google.generativeai as genai

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Clase abstracta para proveedores de LLM"""

    @abstractmethod
    def generate_response(self, prompt):
        """Generar respuesta basada en el prompt"""
        pass


class GeminiProvider(LLMProvider):
    """Proveedor para Gemini AI"""

    def __init__(self, api_key, model_name="gemini-2.0-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self._initialize()

    def _initialize(self):
        """Inicializar la API de Gemini"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini inicializado con modelo {self.model_name}")
            return True
        except Exception as e:
            logger.error(f"Error al inicializar Gemini: {e}", exc_info=True)
            return False

    def generate_response(self, prompt):
        """Generar respuesta usando la API de Gemini"""
        try:
            response = self.model.generate_content(prompt)
            logger.info(f"LLM response: {response.text}")
            return response.text
        except Exception as e:
            logger.error(f"Error al generar respuesta con Gemini: {e}", exc_info=True)
            return "Lo siento, no puedo responder en este momento."


class LLMProviderFactory:
    @staticmethod
    def create_provider(provider_type, config):
        """Crear una instancia de LLMProvider según el tipo"""
        if provider_type.lower() == "gemini":
            api_key = config.llm_api_keys.get("gemini")
            if not api_key:
                logger.error("API key de Gemini no encontrada")
                return None
            return GeminiProvider(api_key)
        # Aquí se pueden agregar más proveedores en el futuro
        else:
            logger.error(f"Proveedor LLM no soportado: {provider_type}")
            return None
