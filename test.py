import argparse
import logging
import json
import os
from config import Config
from managers.prompt_manager import PromptManager
from llm_provider import LLMProviderFactory
from processors.response_processor import ResponseProcessor
from managers.chat_persistence_manager import ChatPersistenceManager
from managers.chat_manager import ChatManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llm_tester")


class LLMTester:
    def __init__(self, config_path=None, llm_type=None):
        # Inicializar configuración
        self.config = Config(config_path)

        # Usar el tipo de LLM especificado o el predeterminado
        self.llm_type = llm_type or self.config.config.get("llm", {}).get(
            "default", "gemini"
        )

        # Inicializar componentes necesarios
        self.chat_persistence_manager = ChatPersistenceManager(self.config)
        self.chat_manager = ChatManager(self.config, self.chat_persistence_manager)
        self.prompt_manager = PromptManager(self.config)
        self.response_processor = ResponseProcessor()

        # Inicializar proveedor LLM
        self.llm_provider = LLMProviderFactory.create_provider(
            self.llm_type, self.config
        )

        if not self.llm_provider:
            logger.error(f"No se pudo inicializar el proveedor LLM: {self.llm_type}")
            raise ValueError(f"Proveedor LLM no válido: {self.llm_type}")

        logger.info(f"Inicializado tester con proveedor LLM: {self.llm_type}")

    def test_response(
        self,
        message,
        contact_name="Test User",
        show_prompt=False,
    ):
        """
        Prueba la respuesta del modelo LLM para un mensaje específico

        Args:
            message (str): Mensaje para procesar
            contact_name (str): Nombre del contacto simulado
            show_prompt (bool): Si se debe mostrar el prompt completo enviado al LLM

        Returns:
            dict: Resultado que incluye la respuesta y metadatos
        """

        # Añadir mensaje al historial
        self.chat_manager.add_messages(
            "Test",
            [
                {
                    "sender": contact_name,
                    "message": message,
                    "date": "2024-01-01",
                    "time": "12:00",
                }
            ],
        )

        # Obtener el historial de chat
        chat_history = self.chat_manager.get_chat_history("Test")
        logger.info(f"History: {chat_history}")

        # Generar prompt completo
        full_prompt = self.prompt_manager.format_prompt("Test", chat_history)

        if show_prompt:
            logger.info(f"Prompt completo:\n{full_prompt}")

        # Obtener respuesta del LLM
        start_time = os.times()
        llm_response = self.llm_provider.generate_response(full_prompt)
        end_time = os.times()
        processing_time = (end_time.user - start_time.user) + (
            end_time.system - start_time.system
        )

        # Procesar respuesta
        processed_response = self.response_processor.process_response(llm_response)

        # Añadir respuesta al historial
        self.chat_manager.add_messages(
            "Test",
            [
                {
                    "sender": "Assistant",
                    "message": processed_response,
                    "date": "2024-01-01",
                    "time": "12:00",
                }
            ],
        )

        return {
            "original_message": message,
            "response": processed_response,
            "processing_time_sec": processing_time,
        }

    def run_interactive_mode(self):
        """Ejecuta un modo interactivo para probar mensajes"""
        chat_id = "interactive_test"
        contact_name = "Interactive User"
        prompt_name = (
            input("Nombre del prompt a usar (vacío para usar el predeterminado): ")
            or None
        )
        show_prompt = input("¿Mostrar prompt completo? (s/n): ").lower() == "s"

        print("\n--- Modo interactivo iniciado (escribe 'salir' para terminar) ---")
        while True:
            user_input = input("\nTú: ")
            if user_input.lower() in ["salir", "exit", "quit"]:
                break

            result = self.test_response(
                user_input,
                contact_name=contact_name,
                show_prompt=show_prompt,
            )

            print(f"\nBot ({self.llm_type}): {result['response']}")
            print(f"Tiempo: {result['processing_time_sec']:.2f}s")

        print("--- Sesión terminada ---")

    def run_batch_test(self, test_file):
        """
        Ejecuta pruebas en lote desde un archivo JSON

        El archivo debe tener el formato:
        [
            {"message": "Hola", "contact_name": "Usuario 1", "chat_id": "chat1", "prompt_name": "default"},
            {"message": "¿Cómo estás?", "contact_name": "Usuario 2"}
        ]
        """
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                test_cases = json.load(f)

            results = []
            for i, test_case in enumerate(test_cases):
                logger.info(f"Ejecutando prueba {i+1}/{len(test_cases)}")

                message = test_case.get("message")
                if not message:
                    logger.warning(f"Prueba {i+1} no tiene mensaje, omitiendo")
                    continue

                result = self.test_response(
                    message,
                    contact_name=test_case.get("contact_name", "Test User"),
                    chat_id=test_case.get("chat_id", f"test_chat_{i}"),
                    prompt_name=test_case.get("prompt_name"),
                    show_prompt=test_case.get("show_prompt", False),
                )
                results.append(result)

                # Mostrar resultado
                print(f"\n--- Resultado prueba {i+1} ---")
                print(f"Mensaje: {message}")
                print(f"Respuesta: {result['response']}")
                print(f"Tiempo: {result['processing_time_sec']:.2f}s")

            # Guardar resultados
            output_file = f"test_results_{self.llm_type}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"Resultados guardados en {output_file}")
            return results

        except Exception as e:
            logger.error(f"Error al ejecutar pruebas en lote: {e}", exc_info=True)
            return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Tester para respuestas del modelo LLM"
    )
    parser.add_argument(
        "--config", help="Ruta al archivo de configuración", default="config.json"
    )
    parser.add_argument("--llm", help="Tipo de LLM a usar (gemini, openai, etc.)")
    parser.add_argument("--test-file", help="Archivo JSON con casos de prueba")
    parser.add_argument(
        "--interactive", action="store_true", help="Ejecutar en modo interactivo"
    )
    parser.add_argument("--message", help="Mensaje único para probar")
    parser.add_argument("--prompt", help="Nombre del prompt a usar")
    parser.add_argument(
        "--show-prompt", action="store_true", help="Mostrar prompt completo"
    )

    args = parser.parse_args()

    try:
        tester = LLMTester(config_path=args.config, llm_type=args.llm)

        if args.interactive:
            tester.run_interactive_mode()
        elif args.test_file:
            tester.run_batch_test(args.test_file)
        elif args.message:
            result = tester.test_response(
                args.message, prompt_name=args.prompt, show_prompt=args.show_prompt
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # Si no se especifica ninguna acción, entrar en modo interactivo
            print("No se especificó ninguna acción. Entrando en modo interactivo.")
            tester.run_interactive_mode()

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
