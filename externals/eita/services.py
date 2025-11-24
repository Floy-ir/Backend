import logging
import os
from . import interfaces
from utils.http_requester import interfaces as http_requester_interfaces

logger = logging.getLogger(__name__)


class EitaService(interfaces.AbstractEitaService):
    """
    Eita service implementation for sending messages via Eita API.
    """
    
    def __init__(self, token: str = None, http_requester: http_requester_interfaces.AbstractHTTPRequester = None):
        """
        Initialize Eita service.
        
        Args:
            token: Eita API token. If not provided, will be read from EITA_TOKEN environment variable.
            http_requester: HTTP requester instance for making API calls.
        """
        self.token = token or os.getenv('EITA_TOKEN', '5768337691:AAGDAe6rjxu1cUgxK4BizYi--Utc3J9v5AU')
        self.base_url = "https://eitaayar.ir/api/app/sendMessage"
        self.http_requester = http_requester
    
    def send_message(self, chat_id: int, text: str) -> bool:
        """
        Send message to Eita user via Eita API.
        
        Args:
            chat_id: The Eita chat ID (user's eita_id as integer)
            text: The message content to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self.http_requester:
            logger.error("HTTP requester is not configured for Eita service")
            return False
            
        try:
            payload = {
                "token": self.token,
                "chat_id": chat_id,
                "text": text
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = self.http_requester.post(
                url=self.base_url,
                json=payload,
                headers=headers,
                timeout=(10, 30),
                parse_response_as_json=True
            )
            
            if response.status_code == 200 and response.content_json:
                result = response.content_json
                if result.get("ok") == True and result.get("result") == "success":
                    logger.info(f"Message sent successfully to Eita user (chat_id: {chat_id})")
                    return True
                else:
                    logger.warning(f"Failed to send message to Eita user (chat_id: {chat_id}): {result}")
                    return False
            else:
                logger.warning(f"HTTP request failed for Eita user (chat_id: {chat_id}): status_code={response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message to Eita user (chat_id: {chat_id}): {str(e)}")
            return False

