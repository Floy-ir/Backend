from abc import ABC
from typing import Optional

class AbstractProxyManager(ABC):
    def get_proxy(self) -> Optional[str]:
        """Get a working proxy"""
        raise NotImplementedError

    def remove_proxy(self, proxy: str) -> None:
        """Remove a proxy from the list"""
        raise NotImplementedError 