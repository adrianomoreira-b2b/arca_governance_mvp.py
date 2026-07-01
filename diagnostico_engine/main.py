import os
from flask import Flask, request, render_template, jsonify
from services.diagnostico_service import DiagnosticoService
from services.notification_service import NotificationService
from infrastructure.providers.email_provider import EmailProvider
from infrastructure.providers.crm_provider import CRMProvider
from infrastructure.logger import logger

app = Flask(__name__)

# Instanciação dos serviços na inicialização (Injeção de Dependência)
# Adicione ou remova provedores aqui conforme sua necessidade comercial
email_provider = EmailProvider()
crm_provider = CRMProvider()

notification_service = NotificationService()
notification_service.registrar_provider(email_provider)
notification_service.registrar_provider(crm_provider)

diagnostico_service = DiagnosticoService(notification_service)

# ROTA 1: Página Inicial (Exibe o Formulário Web)
@app.route('/')
def pagina_inicial():
    logger.info("Carregando página inicial do formulário de diagnóstico.")
    return render_template('index.html')

# ROTA 2: Processamento do Diagnóstico (Recebe o formulário via POST)
@app.route('/diagnostico', methods=['POST'])
def processar_formulario():
    logger.info("Nova requisição de diagnóstico recebida.")
    
    try:
        # Captura os dados enviados pelo formulário HTML
        dados_brutos = request.form.to_dict()
        
        # Se os dados vierem como JSON (ex: chamadas de API/Postman)
        if not dados_brutos and request.is_json:
            dados_brutos = request.get_json()
            
        if not dados_brutos:
            logger.warning("Requisição recebida sem dados válidos.")
            return jsonify({"erro": "Nenhum dado enviado."}), 400

        # Executa o motor estático de cálculo e gera as notificações desacopladas
        resultado = diagnostico_service.executar_fluxo_completo(dados_brutos)
        
        logger.info("Fluxo de diagnóstico processado com sucesso.")
        return jsonify(resultado), 200

    except Exception as e:
        logger.error(f"Erro crítico no processamento do controlador: {str(e)}")
        return jsonify({"erro": "Ocorreu um erro interno ao processar seu diagnóstico."}), 500

if __name__ == '__main__':
    # Configuração para rodar localmente se necessário
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)