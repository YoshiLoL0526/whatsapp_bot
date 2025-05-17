# 🤖 WhatsApp Bot

Un bot de automatización para WhatsApp basado en Python, diseñado para responder automáticamente a los mensajes recibidos a través de **WhatsApp Web** haciendo uso de **Selenium**.

## ⚠️ Aviso

Este bot es únicamente con fines educativos.
Automatizar o enviar mensajes masivos puede violar los Términos de servicio de WhatsApp.

## ✨ ¿Qué hace?

Este bot actualmente permite:

- 📩 Responder automáticamente a mensajes de texto entrantes
- 🧾 Usar plantillas personalizadas de mensajes
- 🌐 Integración directa con WhatsApp Web

> 🔒 **Nota:** Por ahora, solo se admiten mensajes en **texto plano**.  
> 🧠 Próximamente: soporte para **audios**, **imágenes**, y funcionalidades avanzadas como:
>
> - Guardar mensajes importantes 📌  
> - Notificar al propietario del bot 🔔  
> - Generar resúmenes inteligentes de conversaciones 🧾  

## ⚙️ Requisitos

- Python 3.8 o superior 🐍
- Navegador Chrome o Firefox 🌐
- [Selenium WebDriver](https://www.selenium.dev/documentation/webdriver/)
- Una cuenta activa de WhatsApp 📱

## 🚀 Instalación

```bash
# Clona este repositorio
git clone https://github.com/yoshilol0526/whatsapp_bot.git

# Instala las dependencias
pip install -r requirements.txt
```

## 🔧 Configuración

1. Crea un archivo .env en la raíz del proyecto.
2. Añade tus variables de entorno:

```env
CHROME_DRIVER_PATH=path/to/chromedriver
DEFAULT_WAIT_TIME=20
GEMINI_API_KEY=your-gemini-api-key
```

## ▶️ Uso

```bash
python bot.py
```

## 🤝 Contribuciones

¡Tu ayuda es bienvenida!

1. Haz un fork del repositorio
2. Crea una rama nueva
3. Realiza tus cambios
4. Envía un pull request

## 📄 Licencia

Este proyecto está licenciado bajo la MIT License.
