import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)


class WhatsAppClient:
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config

    def login(self, session_manager):
        """Iniciar sesión en WhatsApp Web"""
        if not session_manager.load_session():
            self.driver.get("https://web.whatsapp.com/")
            logger.info("Escanea el código QR para iniciar sesión")

            # Esperar a que se cargue la página principal después del login
            try:
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@aria-label='Lista de chats']")
                    )
                )
                session_manager.save_session()
                logger.info("Sesión iniciada y guardada correctamente")
                return True
            except Exception as e:
                logger.error(f"Error al iniciar sesión: {e}", exc_info=True)
                return False
        else:
            self.driver.get("https://web.whatsapp.com/")
            # Esperar a que se cargue la página principal
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@aria-label='Lista de chats']")
                    )
                )
                logger.info("Sesión restaurada correctamente")
                return True
            except Exception as e:
                logger.error(f"Error al restaurar sesión: {e}", exc_info=True)
                return False

    def get_unread_chats(self):
        """Obtener chats con mensajes no leídos"""
        try:
            unread_chats = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//div[@role='listitem']//span[contains(@aria-label, 'mensaje') and contains(@aria-label, 'no leído')]/../../../..",
                    )
                )
            )
            return unread_chats
        except Exception as e:
            logger.debug(f"No se encontraron chats no leídos: {e}")
            return []

    def open_chat(self, chat_element):
        """Abrir un chat específico"""
        try:
            chat_element.click()
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Error al abrir chat: {e}", exc_info=True)
            return False

    def get_messages(self):
        """Obtener mensajes del chat actual con información del remitente"""
        try:
            # Esperar a que carguen los mensajes
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='main']"))
            )

            # Obtener mensajes recibidos (message-in)
            message_elements = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'message-in')]"
            )
            messages = []

            for element in message_elements[-10:]:
                try:
                    # Obtener el texto del mensaje
                    message_text = element.find_element(
                        By.XPATH, ".//span[contains(@class, 'selectable-text')]"
                    ).text

                    # Obtener el pre-plain-text que contiene la información del remitente
                    pre_plain_text = element.find_element(
                        By.XPATH, ".//div[contains(@class, 'copyable-text')]"
                    ).get_attribute("data-pre-plain-text")

                    # Extraer la hora, fecha y nombre del remitente del pre-plain-text
                    # El formato es "[hora, fecha] Nombre: "
                    time_date = pre_plain_text[1:].split("]")[0].strip()  # Remove first '[' and split by ']'
                    time, date = time_date.split(", ")
                    sender = pre_plain_text.split("]")[-1].split(":")[0].strip()
                    
                    messages.append({
                        "sender": sender,
                        "time": time,
                        "date": date,
                        "message": message_text
                    })
                except Exception as e:
                    logger.debug(f"Error al procesar mensaje individual: {e}")
                    continue

            return messages
        except Exception as e:
            logger.error(f"Error al obtener mensajes: {e}", exc_info=True)
            return []

    def get_chat_name(self):
        """Obtener el nombre del chat actual"""
        try:
            name_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@id='main']/header/div[2]/div[1]/div/div/div/span[1]",
                    )
                )
            )
            return name_element.get_attribute("title")
        except Exception as e:
            logger.error(f"Error al obtener nombre del chat: {e}", exc_info=True)
            return "Unknown"

    def send_message(self, message):
        """Enviar un mensaje al chat actual"""
        try:
            input_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@role='textbox' and @contenteditable='true' and @aria-label='Escribe un mensaje']",
                    )
                )
            )

            input_box.clear()
            # Convert non-BMP characters to their closest BMP equivalents
            encoded_message = "".join(
                char if ord(char) < 0x10000 else "" for char in message
            )
            input_box.send_keys(encoded_message)
            time.sleep(1)

            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Enviar']"))
            )
            send_button.click()

            return True
        except Exception as e:
            logger.error(f"Error al enviar mensaje: {e}", exc_info=True)
            return False

    def is_chat_loaded(self):
        """Verificar si la interfaz de chat está cargada correctamente"""
        try:
            # Verificar si el panel de conversación está presente
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "main"))
            )
            time.sleep(1)
            return True
        except:
            return False

    def refresh_page(self):
        """Refrescar la página cuando hay problemas de carga"""
        try:
            self.driver.refresh()
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@aria-label='Lista de chats']")
                )
            )
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Error al refrescar página: {e}", exc_info=True)
            return False

    def close_current_chat(self):
        """Cerrar el chat actual"""
        try:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Error al cerrar chat: {e}", exc_info=True)
            return False
