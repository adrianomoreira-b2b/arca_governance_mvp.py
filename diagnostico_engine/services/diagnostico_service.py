from domain import score_rules
from services.notification_service import NotificationService
from infrastructure.logger import get_logger

logger = get_logger("DiagnosticoService")

class DiagnosticoService:
    """
    Core da aplicação (Caso de Uso). Orquestra as regras e delega notificações.
    """
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def executar_fluxo_completo(self, dados: dict, contato_usuario: str) -> dict:
        logger.info("Iniciando processamento de novo diagnóstico.")
        
        # 1. Executa regras puras de domínio
        score = score_rules.calcular_pontuacao_pura(dados)
        perfil = score_rules.definir_perfil(score)
        
        resultado = {
            "score": score,
            "perfil": perfil,
            "status": "Processado com sucesso"
        }
        
        # 2. Desacopla o envio enviando o resultado para a camada de notificação
        self.notification_service.notificar_todos(
            destinatario=contato_usuario, 
            dados_notificacao=resultado
        )
        
        return resultado
    