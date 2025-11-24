import logging
import os
from . import interfaces
from utils.http_requester import interfaces as http_requester_interfaces

logger = logging.getLogger(__name__)


class BaleService(interfaces.AbstractBaleService):
    """
    Bale service implementation for sending messages via Bale API.
    """
    
    def __init__(self, token: str = None, http_requester: http_requester_interfaces.AbstractHTTPRequester = None):
        """
        Initialize Bale service.
        
        Args:
            token: Bale API token. If not provided, will be read from BALE_TOKEN environment variable.
            http_requester: HTTP requester instance for making API calls.
        """
        self.token = token or os.getenv('BALE_TOKEN', '')
        self.base_url = "https://tapi.bale.ai/bot{}/sendMessage"
        self.http_requester = http_requester
    
    def send_message(self, chat_id: int, text: str) -> bool:
        """
        Send message to Bale user via Bale API.
        
        Args:
            chat_id: The Bale chat ID (user's bale_id as integer)
            text: The message content to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self.http_requester:
            logger.error("HTTP requester is not configured for Bale service")
            return False
            
        if not self.token:
            logger.error("Bale token is not configured")
            return False
            
        try:
            # Format the base URL with token
            url = self.base_url.format(self.token)
            
            payload = {
                "chat_id": chat_id,
                "text": text
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = self.http_requester.post(
                url=url,
                json=payload,
                headers=headers,
                timeout=(10, 30),
                parse_response_as_json=True
            )
            
            if response.status_code == 200 and response.content_json:
                result = response.content_json
                if result.get("ok") == True:
                    logger.info(f"Message sent successfully to Bale user (chat_id: {chat_id})")
                    return True
                else:
                    logger.warning(f"Failed to send message to Bale user (chat_id: {chat_id}): {result}")
                    return False
            else:
                logger.warning(f"HTTP request failed for Bale user (chat_id: {chat_id}): status_code={response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message to Bale user (chat_id: {chat_id}): {str(e)}")
            return False

