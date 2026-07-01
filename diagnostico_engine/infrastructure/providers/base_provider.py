from abc import ABC, abstractmethod
from typing import Any

class NotificationProvider(ABC):
    """
    Interface base (Contrato) para todos os providers de envio.
    """
    @abstractmethod
    def send(self, destinatario: str, mensagem: Any) -> bool:
        pass