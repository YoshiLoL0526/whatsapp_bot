import os
import pickle
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self, config, driver):
        self.config = config
        self.driver = driver
        self.session_path = config.session_path

    def load_session(self):
        """Cargar sesión de WhatsApp si existe"""
        if os.path.exists(self.session_path):
            try:
                with open(self.session_path, "rb") as f:
                    cookies = pickle.load(f)

                self.driver.get("https://web.whatsapp.com/")
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                logger.info("Sesión cargada correctamente")
                return True
            except Exception as e:
                logger.error(f"Error al cargar sesión: {e}", exc_info=True)
        return False

    def save_session(self):
        """Guardar sesión actual de WhatsApp"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.session_path, "wb") as f:
                pickle.dump(cookies, f)
            logger.info("Sesión guardada correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al guardar sesión: {e}", exc_info=True)
            return False
