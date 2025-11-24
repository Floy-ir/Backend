import abc


class AbstractBaleService(abc.ABC):
    """
    Bale service interface for sending messages to Bale users.
    """

    @abc.abstractmethod
    def send_message(self, chat_id: int, text: str) -> bool:
        """
        Send message to Bale user.
        
        Args:
            chat_id: The Bale chat ID (user's bale_id as integer)
            text: The message content to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        raise NotImplementedError

