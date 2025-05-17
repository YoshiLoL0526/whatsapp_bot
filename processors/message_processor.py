import logging

logger = logging.getLogger(__name__)


class MessageProcessor:
    def __init__(
        self,
        whatsapp_client,
        chat_manager,
        prompt_manager,
        llm_provider,
        response_processor,
    ):
        self.whatsapp_client = whatsapp_client
        self.chat_manager = chat_manager
        self.prompt_manager = prompt_manager
        self.llm_provider = llm_provider
        self.response_processor = response_processor

    def process_unread_chats(self):
        """Procesar todos los chats no leídos"""
        try:
            unread_chats = self.whatsapp_client.get_unread_chats()
            logger.info(f"Chats no leídos encontrados: {len(unread_chats)}")

            for chat in unread_chats:
                try:
                    if self.whatsapp_client.open_chat(chat):
                        # Verificar si el chat se cargó correctamente
                        if not self.whatsapp_client.is_chat_loaded():
                            logger.warning(
                                "El chat no se cargó correctamente, refrescando página..."
                            )
                            self.whatsapp_client.refresh_page()
                            continue

                        chat_name = self.whatsapp_client.get_chat_name()
                        logger.info(f"Procesando chat: {chat_name}")

                        messages = self.whatsapp_client.get_messages()
                        if messages:
                            logger.info(
                                f"Mensajes recibidos: {len(messages)} - Último: {messages[-1]['message'][:50]}..."
                            )

                            # Actualizar historial de chat
                            self.chat_manager.add_messages(chat_name, messages)

                            # Obtener historial completo para contexto
                            chat_history = self.chat_manager.get_chat_history(chat_name)

                            # Crear prompt para el LLM
                            prompt = self.prompt_manager.format_prompt(
                                chat_name, chat_history
                            )

                            # Obtener respuesta del LLM
                            raw_response = self.llm_provider.generate_response(prompt)

                            # Procesar la respuesta del asistente virtual
                            user_message = self.response_processor.process_response(
                                raw_response
                            )

                            # Si no se logró extraer un mensaje para el usuario, usar la respuesta completa
                            if not user_message.strip():
                                user_message = raw_response

                            # Enviar respuesta procesada al usuario
                            success = self.whatsapp_client.send_message(user_message)

                            if success:
                                logger.info(f"Respuesta enviada a {chat_name}")
                            else:
                                logger.error(
                                    f"Falló el envío de respuesta a {chat_name}"
                                )
                        else:
                            logger.warning(
                                f"No se encontraron mensajes en el chat {chat_name}"
                            )

                except Exception as e:
                    logger.error(f"Error procesando chat: {e}", exc_info=True)
                    continue
                finally:
                    # Cerrar el chat actual
                    self.whatsapp_client.close_current_chat()

            return True
        except Exception as e:
            logger.error(f"Error general en process_unread_chats: {e}", exc_info=True)
            return False
