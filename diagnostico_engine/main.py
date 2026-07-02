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