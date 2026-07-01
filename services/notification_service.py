from typing import List, Dict, Any
from infrastructure.providers.base_provider import NotificationProvider
from infrastructure.logger import get_logger

logger = get_logger("NotificationService")

class NotificationService:
    """
    Orquestrador da camada de notificação. Suporta múltiplos providers (DIP).
    """
    def __init__(self, providers: List[NotificationProvider] = None):
        self.providers = providers or []

    def adicionar_provider(self, provider: NotificationProvider):
        self.providers.append(provider)

    def notificar_todos(self, destinatario: str, dados_notificacao: Dict[str, Any]):
        logger.info(f"Iniciando disparos multicanais para {destinatario}.")
        resultados = {}
        
        # Iteração preparada para execução paralela/assíncrona no futuro
        for provider in self.providers:
            nome_provider = provider.__class__.__name__
            try:
                sucesso = provider.send(destinatario, dados_notificacao)
                resultados[nome_provider] = sucesso
                logger.info(f"Status do {nome_provider}: {'Sucesso' if sucesso else 'Falha'}")
            except Exception as e:
                logger.error(f"Erro crítico no provider {nome_provider}: {str(e)}")
                resultados[nome_provider] = False
                
        return resultados
    