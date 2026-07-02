import os
from flask import Flask, request, render_template, jsonify

from services.diagnostico_service import DiagnosticoService
from services.notification_service import NotificationService

from infrastructure.providers.email_provider import EmailProvider
from infrastructure.providers.crm_provider import CrmProvider
from infrastructure.logger import get_logger

logger = get_logger("Main")

app = Flask(__name__)

# Providers
email_provider = EmailProvider()
crm_provider = CrmProvider()

# Notification Service
notification_service = NotificationService()
notification_service.adicionar_provider(email_provider)
notification_service.adicionar_provider(crm_provider)

# Diagnóstico
diagnostico_service = DiagnosticoService(notification_service)
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/processar", methods=["POST"])
def processar_formulario():
    try:
        dados_brutos = request.get_json()

        if not dados_brutos:
            return jsonify({"erro": "Nenhum dado enviado."}), 400

        resultado = diagnostico_service.executar_fluxo_completo(dados_brutos)

        return jsonify(resultado), 200

    except Exception as e:
        logger.error(str(e))
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)