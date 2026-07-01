from infrastructure.providers.base_provider import NotificationProvider
from infrastructure.logger import get_logger

logger = get_logger("EmailProvider")

class EmailProvider(NotificationProvider):
    def __init__(self, smtp_config: dict = None):
        self.config = smtp_config or {"host": "localhost", "port": 25}

    def send(self, destinatario: str, mensagem: any) -> bool:
        # Isolamento do SMTP. Preparado para virar async no futuro.
        logger.info(f"Conectando ao SMTP {self.config['host']}...")
        logger.info(f"Enviando e-mail de diagnóstico para: {destinatario}")
        # Lógica simulada de envio de e-mail
        return True
    