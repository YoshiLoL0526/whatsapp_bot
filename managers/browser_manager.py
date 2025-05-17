import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class BrowserManager:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.service = None

    def initialize_browser(self):
        """Inicializa el navegador con las opciones configuradas"""
        try:
            # Configurar opciones de Chrome
            chrome_options = Options()
            chrome_options.add_argument(
                f"--user-data-dir={self.config.browser_data_path}"
            )
            chrome_options.add_argument("--profile-directory=Default")
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--v=1")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # Aplicar configuración adicional desde el archivo de configuración
            browser_config = self.config.config.get("browser", {})
            if browser_config.get("headless", False):
                chrome_options.add_argument("--headless")

            window_size = browser_config.get("window_size")
            if window_size:
                chrome_options.add_argument(f"--window-size={window_size}")

            # Configurar servicio y logs
            self.service = Service(ChromeDriverManager().install())
            self.service.log_path = os.path.join(
                self.config.logs_path, "chromedriver.log"
            )

            # Inicializar el navegador
            self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
            return True
        except Exception as e:
            logger.error(f"Error al inicializar el navegador: {e}", exc_info=True)
            return False

    def close(self):
        """Cierra el navegador"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error al cerrar el navegador: {e}", exc_info=True)
