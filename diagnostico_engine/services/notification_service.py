import threading
from typing import List, Dict, Any
from infrastructure.providers.base_provider import NotificationProvider
from infrastructure.logger import get_logger

logger = get_logger("NotificationService")

class NotificationService:
    def __init__(self, providers: List[NotificationProvider] = None):
        self.providers = providers or []

    def adicionar_provider(self, provider: NotificationProvider):
        self.providers.append(provider)

    def _executar_disparo_background(self, destinatario: str, dados_notificacao: Dict[str, Any]):
        """
        Método interno executado de forma assíncrona (Thread/Fila).
        """
        logger.info(f"[BACKGROUND] Iniciando disparos paralelos para {destinatario}...")
        for provider in self.providers:
            nome_provider = provider.__class__.__name__
            try:
                sucesso = provider.send(destinatario, dados_notificacao)
                logger.info(f"[BACKGROUND] {nome_provider}: {'Sucesso' if sucesso else 'Falha'}")
            except Exception as e:
                logger.error(f"[BACKGROUND] Erro crítico no {nome_provider}: {str(e)}")

    def notificar_todos(self, destinatario: str, dados_notificacao: Dict[str, Any]):
        """
        Inicia os disparos em uma thread separada para não bloquear a resposta HTTP.
        """
        # Preparado para evoluir para Celery/Redis facilmente substituindo esta chamada
        worker = threading.Thread(
            target=self._executar_disparo_background, 
            args=(destinatario, dados_notificacao)
        )
        worker.start()
        logger.info("Disparos de notificação encaminhados para segundo plano.")
        