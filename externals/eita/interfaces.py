import abc


class AbstractEitaService(abc.ABC):
    """
    Eita service interface for sending messages to Eita users.
    """

    @abc.abstractmethod
    def send_message(self, chat_id: int, text: str) -> bool:
        """
        Send message to Eita user.
        
        Args:
            chat_id: The Eita chat ID (user's eita_id as integer)
            text: The message content to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        raise NotImplementedError

