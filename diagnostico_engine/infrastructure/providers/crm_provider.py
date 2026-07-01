from infrastructure.providers.base_provider import NotificationProvider
from infrastructure.logger import get_logger

logger = get_logger("CrmProvider")

class CrmProvider(NotificationProvider):
    """
    Adapter para envio de leads qualificados em tempo real para o CRM (Ex: Kommo).
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "MOCK_CRM_KEY_12345"

    def send(self, destinatario: str, mensagem: any) -> bool:
        logger.info(f"Conectando à API do CRM com chave: {self.api_key[:5]}*****")
        logger.info(f"Criando cartão/lead para [{destinatario}] com perfil: {mensagem.get('perfil')}")
        # Aqui entraria a requisição HTTP (ex: requests.post ou httpx.post)
        return True
    