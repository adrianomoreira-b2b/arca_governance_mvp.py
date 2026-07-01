import time
from flask import Flask, request, jsonify, render_template
from infrastructure.providers.email_provider import EmailProvider
from infrastructure.providers.crm_provider import CrmProvider
from services.notification_service import NotificationService
from services.diagnostico_service import DiagnosticoService
from infrastructure.logger import get_logger

logger = get_logger("MainController")
app = Flask(__name__)

# --- INSTANCIAÇÃO DAS MELHORIAS (INJEÇÃO DE DEPENDÊNCIA) ---
email_prov = EmailProvider()
crm_prov = CrmProvider(api_key="KOMMO_PROD_ABC123") # Nova melhoria de CRM injetada! 

# Configurando múltiplos canais simultâneos [cite: 9, 21]
notif_service = NotificationService(providers=[email_prov, crm_prov])
diagnostico_service = DiagnosticoService(notification_service=notif_service)

@app.route('/diagnostico', methods=['POST'])
def processar_diagnostico():
    inicio = time.time()
    logger.info("Nova requisição recebida.")
    
    dados_requisicao = request.json or request.form.to_dict()
    contato = dados_requisicao.pop("email_usuario", "cliente@empresa.com")
    
    # Executa lógica de negócio rápida e delega o envio assíncrono 
    resultado_final = diagnostico_service.executar_fluxo_completo(dados_requisicao, contato)
    
    tempo_execucao = (time.time() - inicio) * 1000
    logger.info(f"Resposta HTTP gerada em {tempo_execucao:.2f}ms. Usuário liberado!") [cite: 21]
    
    return jsonify({
        "mensagem": "Seu diagnóstico foi processado. Os resultados estão sendo enviados pelos canais digitais.",
        "resultado": resultado_final,
        "performance_ms": round(tempo_execucao, 2)
    }), 200

if __name__ == '__main__':
    app.run(debug=True)