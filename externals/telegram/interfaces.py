import abc


class AbstractTelegramService(abc.ABC):
    """
    Telegram service interface for sending messages to Telegram users.
    """

    @abc.abstractmethod
    def send_message(self, chat_id: int, text: str) -> bool:
        """
        Send message to Telegram user.
        
        Args:
            chat_id: The Telegram chat ID (user's telegram_id as integer)
            text: The message content to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        raise NotImplementedError

