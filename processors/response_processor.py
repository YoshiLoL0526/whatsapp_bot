import re
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class ResponseProcessor:
    """
    Procesa respuestas del LLM que contienen formato estructurado,
    separando acciones a ejecutar y mensajes para el usuario.
    """

    def __init__(self):
        self.message_pattern = re.compile(r"<Message>(.*?)</Message>", re.DOTALL)
        self.xml_block_pattern = re.compile(r"```(?:xml)?\s*((?:<[\s\S]*?>)[\s\S]*?(?:<\/[\s\S]*?>))```")

    def process_response(self, response: str) -> List[str]:
        """
        Procesa una respuesta que puede contener XML, extrayendo los mensajes del usuario.
        Busca tanto en bloques de código XML como directamente en el texto.
        """
        # Comprobar si hay bloques de código XML
        xml_blocks = self.xml_block_pattern.findall(response)

        # Si encontramos bloques XML, procesarlos primero
        messages = []
        if xml_blocks:
            for xml_block in xml_blocks:
                block_messages = self._extract_messages_from_xml(xml_block)
                if block_messages:
                    messages.extend(block_messages)

        # Si no encontramos mensajes en bloques de código, buscar directamente en el texto
        if not messages:
            messages = self._extract_messages_from_xml(response)

        # Si aún no hay mensajes, usar regex como último recurso
        if not messages:
            messages = self.message_pattern.findall(response)

        return "\n".join([msg.strip() for msg in messages if msg.strip()])

    def _extract_messages_from_xml(self, xml_text: str) -> List[str]:
        """
        Extrae mensajes de un texto XML utilizando ET.
        """
        # Limpiar y preparar el XML
        clean_xml = self._ensure_root_node(xml_text)
        
        try:
            root = ET.fromstring(clean_xml)
            # Buscar etiquetas Message en cualquier nivel de profundidad
            messages = []
            
            # Primer intento: buscar en la estructura esperada según la plantilla
            message_elements = root.findall('.//Message')
            if message_elements:
                for msg_elem in message_elements:
                    if msg_elem.text:
                        messages.append(msg_elem.text)
            
            return messages
            
        except ET.ParseError as e:
            logger.warning(f"Error al analizar XML: {e}")
            # Intentar con regex como fallback
            return self.message_pattern.findall(xml_text)

    def _ensure_root_node(self, xml_content: str) -> str:
        """Asegura que el XML tenga un nodo raíz"""
        xml_content = xml_content.strip()
        
        # Si está vacío o no comienza con <, envolverlo en un nodo raíz
        if not xml_content or not xml_content.startswith("<"):
            return f"<Response>{xml_content}</Response>"

        # Verificar si ya tiene un nodo raíz único
        if re.search(r"^\s*<[\w:]+[^>]*>.*</[\w:]+>\s*$", xml_content, re.DOTALL):
            return xml_content
        
        # Si parece contener múltiples elementos raíz, envolverlos
        return f"<Response>{xml_content}</Response>"
